"""Check an alignment bundle against the pinned sources without changing it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import tempfile

import numpy as np

from export_alignment import export_bundle, transform_pdb
from structure_evidence import ValidationError, parse_pdb, sha256, verify_inputs

PINNED_MANIFEST_SHA256 = "03969a576ba2b0259fbadb568195a618f5931a519b18e8ae3359fbf3d6cd5527"
BUNDLE_FILES = {"aligned_prediction.pdb", "transform.json", "receipt.json"}
MAX_FILE_BYTES = 2 * 1024 * 1024
NUMERIC_TOLERANCE = 1e-10


def strict_json(raw: bytes, name: str):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValidationError(f"Duplicate JSON key in {name}: {key}")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValidationError(f"Nonfinite JSON number in {name}: {value}")

    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                       parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise ValidationError(f"{name} must be a JSON object")
    return value


def compare_value(actual, expected, path):
    """Check schema/values; tolerate only tiny floating-point recomputation drift."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            raise ValidationError(f"Field set mismatch: {path}")
        for key in expected:
            compare_value(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ValidationError(f"List mismatch: {path}")
        for i, (a, e) in enumerate(zip(actual, expected)):
            compare_value(a, e, f"{path}[{i}]")
    elif type(expected) is float:
        if (type(actual) not in (int, float) or not np.isfinite(actual)
                or abs(actual - expected) > NUMERIC_TOLERANCE):
            raise ValidationError(f"Numeric mismatch: {path}")
    elif type(actual) is not type(expected) or actual != expected:
        raise ValidationError(f"Value mismatch: {path}")


def verify_bundle(data_dir: Path, bundle_dir: Path, strict_runtime=False):
    data_dir, bundle_dir = Path(data_dir), Path(bundle_dir)
    if sha256(data_dir / "provenance.json") != PINNED_MANIFEST_SHA256:
        raise ValidationError("Source manifest does not match the pinned case fingerprint")
    verify_inputs(data_dir)
    if not bundle_dir.is_dir() or bundle_dir.is_symlink():
        raise ValidationError("Bundle must be a real directory")
    names = {path.name for path in bundle_dir.iterdir()}
    if not BUNDLE_FILES <= names or names - BUNDLE_FILES - {"README.md"}:
        raise ValidationError("Bundle requires model, transform and receipt; only an optional README.md is allowed")
    blobs = {}
    for name in sorted(BUNDLE_FILES):
        path = bundle_dir / name
        if path.is_symlink() or not path.is_file():
            raise ValidationError(f"Bundle member must be a regular file: {name}")
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ValidationError(f"Bundle member exceeds 2 MiB limit: {name}")
        blobs[name] = path.read_bytes()
    receipt = strict_json(blobs["receipt.json"], "receipt.json")
    transform = strict_json(blobs["transform.json"], "transform.json")
    threshold = transform.get("fit_min_plddt")
    if type(threshold) not in (int, float) or not np.isfinite(threshold) or not 0 <= threshold <= 100:
        raise ValidationError("fit_min_plddt must be a finite number from 0 through 100")

    derived = {name: {"sha256": hashlib.sha256(blobs[name]).hexdigest(), "bytes": len(blobs[name])}
               for name in ("aligned_prediction.pdb", "transform.json")}
    compare_value(receipt.get("derived_files"), derived, "receipt.derived_files")

    # Recompute the fit from pinned original data, not from bundle coordinates.
    # A temporary export also defines the exact version-1 field contract.
    with tempfile.TemporaryDirectory(prefix="structure-verify-") as temporary:
        fresh = Path(temporary) / "alignment"
        expected_receipt = export_bundle(data_dir, fresh, float(threshold))
        expected_transform = strict_json((fresh / "transform.json").read_bytes(), "recomputed transform")
    compare_value(transform, expected_transform, "transform")
    if set(receipt) != set(expected_receipt):
        raise ValidationError("Field set mismatch: receipt")
    for key in expected_receipt:
        if key not in {"runtime", "derived_files"}:
            compare_value(receipt[key], expected_receipt[key], f"receipt.{key}")

    runtime = receipt["runtime"]
    if (not isinstance(runtime, dict) or set(runtime) != {"python", "numpy"}
            or any(not isinstance(v, str) or not re.fullmatch(r"\d+\.\d+\.\d+(?:[a-zA-Z0-9.+-]*)", v)
                   for v in runtime.values())):
        raise ValidationError("Runtime metadata must contain Python and NumPy version strings")
    current_runtime = {"python": platform.python_version(), "numpy": np.__version__}
    runtime_matches = runtime == current_runtime
    if strict_runtime and not runtime_matches:
        raise ValidationError("Recorded runtime differs from the verifier runtime")

    expected_text, _ = transform_pdb((data_dir / "AF-P00918-F1-model_v6.pdb").read_bytes().decode("ascii"),
                                     transform["rotation"], transform["translation"])
    if blobs["aligned_prediction.pdb"] != expected_text.encode("ascii"):
        raise ValidationError("Model differs from pinned atoms transformed with the verified matrix")
    # The source files are expected to remain unchanged throughout this check.
    verify_inputs(data_dir)
    return {
        "schema_version": 1,
        "verified": True,
        "source_manifest_sha256": PINNED_MANIFEST_SHA256,
        "verified_bundle_sha256": {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(blobs.items())},
        "predicted_atoms": len(parse_pdb(expected_text)),
        "fit_residues": len(transform["fit_uniprot_positions"]),
        "evaluation_residues": len(transform["evaluation_uniprot_positions"]),
        "fit_min_plddt": threshold,
        "numeric_recomputation_tolerance": NUMERIC_TOLERANCE,
        "recorded_runtime": runtime,
        "current_runtime": current_runtime,
        "runtime_matches_current": runtime_matches,
        "runtime_metadata_authenticated": False,
        "strict_runtime_requested": bool(strict_runtime),
        "limits": "Checks pinned-case file integrity and computational consistency; not authorship, a digital signature, independent method validation, or biological function. An optional README is not verified.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--strict-runtime", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable report to stdout")
    args = parser.parse_args(argv)
    try:
        report = verify_bundle(args.data_dir, args.bundle_dir, args.strict_runtime)
    except (ValidationError, OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        parser.exit(2, f"Verification stopped: {error}\n")
    if args.json:
        print(json.dumps(report, indent=2, allow_nan=False))
    else:
        print(f"Verified {report['predicted_atoms']} atoms; {report['fit_residues']} fit / {report['evaluation_residues']} evaluation residues.")
        print(f"Recorded runtime matches current: {report['runtime_matches_current']} (metadata is not authenticated).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
