"""Export the pinned prediction in the experimental frame, with an audit receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import tempfile

import numpy as np

from structure_evidence import ValidationError, comparison, parse_pdb, sha256, verify_inputs


def transform_pdb(text, rotation, translation):
    """Change Cartesian coordinates only; remove obsolete frame placeholders."""
    rotation = np.asarray(rotation, dtype=float)
    translation = np.asarray(translation, dtype=float)
    if (rotation.shape != (3, 3) or translation.shape != (3,)
            or not np.isfinite(rotation).all() or not np.isfinite(translation).all()
            or not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-10, rtol=0)
            or not np.isclose(np.linalg.det(rotation), 1, atol=1e-10, rtol=0)):
        raise ValidationError("Export requires a finite proper rigid transform")
    parse_pdb(text)  # Reuse numeric, occupancy, and single-model validation.
    result, removed = [], []
    for line in text.splitlines(keepends=True):
        kind = line[:6].strip()
        if kind in {"ANISOU", "SIGATM", "SIGUIJ"} or kind.startswith("MTRIX"):
            raise ValidationError(f"Export does not transform {kind} records")
        if kind == "CRYST1" or kind.startswith(("SCALE", "ORIGX")):
            removed.append(kind)
            continue
        if kind in {"ATOM", "HETATM"}:
            original = np.array([float(line[i:i+8]) for i in (30, 38, 46)])
            xyz = original @ rotation + translation
            fields = [f"{value:8.3f}" for value in xyz]
            if any(len(field) != 8 for field in fields):
                raise ValidationError("Transformed coordinate exceeds PDB 8.3 field width")
            line = line[:30] + "".join(fields) + line[54:]
        result.append(line)
    remarks = [
        "REMARK 900 DERIVED RIGID FIT TO 2CBA A; NOT A NEW STRUCTURE PREDICTION.\n",
        "REMARK 900 COORDINATES IN ANGSTROMS; B COLUMN RETAINS ORIGINAL PLDDT.\n",
        "REMARK 900 CRYST1/SCALE/ORIGX PLACEHOLDERS REMOVED; SEE TRANSFORM.JSON.\n",
        "REMARK 900 TRAINING/TEMPLATE OVERLAP CANNOT BE EXCLUDED.\n",
    ]
    # Keep title/source sections before REMARK and sequence/coordinate sections
    # after it, as in the pinned PDB file's record order.
    later_records = {"DBREF", "DBREF1", "DBREF2", "SEQADV", "SEQRES", "MODRES",
                     "HET", "HETNAM", "HETSYN", "FORMUL", "HELIX", "SHEET",
                     "SSBOND", "LINK", "CISPEP", "SITE", "MODEL", "ATOM", "HETATM", "END"}
    insert = next((i for i, line in enumerate(result) if line[:6].strip() in later_records), len(result))
    result[insert:insert] = remarks
    return "".join(result), removed


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def export_bundle(data_dir, output_dir, fit_min_plddt=0.0):
    """Publish a new complete directory; refuse any pre-existing destination."""
    data_dir, output_dir = Path(data_dir), Path(output_dir)
    if output_dir.resolve() == data_dir.resolve() or data_dir.resolve() in output_dir.resolve().parents:
        raise ValidationError("Export destination must be outside source data")
    if output_dir.exists() or output_dir.is_symlink():
        raise ValidationError("Export destination already exists; choose a new directory")
    result = comparison(data_dir, fit_min_plddt)
    source_name = "AF-P00918-F1-model_v6.pdb"
    text, removed = transform_pdb((data_dir / source_name).read_bytes().decode("ascii"),
                                  result["rotation"], result["translation"])
    transform = {
        "schema_version": 1,
        "convention": "Row vectors: aligned_xyz = original_xyz @ rotation + translation",
        "coordinate_units": "angstrom",
        "source": source_name,
        "target": "2cba.pdb chain A",
        "rotation": result["rotation"].tolist(),
        "translation": result["translation"].tolist(),
        "fit_min_plddt": float(fit_min_plddt),
        "fit_uniprot_positions": [row["uniprot_position"] for row in result["residues"] if row["included_in_fit"]],
        "evaluation_uniprot_positions": result["matched_positions"],
        "fit_rmsd_A": result["summary"]["fit_rmsd_A"],
        "all_matched_ca_rmsd_A": result["summary"]["all_matched_ca_rmsd_A"],
        "coordinate_decimals_in_pdb": 3,
        "removed_frame_records": removed,
        "interpretation": result["summary"]["interpretation"],
    }
    manifest = verify_inputs(data_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".alignment_export_", dir=output_dir.parent) as temporary:
        staged = Path(temporary) / "bundle"
        staged.mkdir()
        (staged / "aligned_prediction.pdb").write_bytes(text.encode("ascii"))
        write_json(staged / "transform.json", transform)
        receipt = {
            "schema_version": 1,
            "source_manifest_sha256": sha256(data_dir / "provenance.json"),
            "source_sha256": {item["path"]: item["sha256"] for item in manifest["files"]},
            "code_sha256": {name: sha256(Path(__file__).parent / name)
                            for name in ("export_alignment.py", "structure_evidence.py")},
            "runtime": {"python": platform.python_version(), "numpy": np.__version__},
            "derived_files": {name: {"sha256": sha256(staged / name), "bytes": (staged / name).stat().st_size}
                              for name in ("aligned_prediction.pdb", "transform.json")},
            "notes": ["Only coordinate columns change in ATOM/HETATM records; original pLDDT is retained.",
                      "Original source files are never overwritten.",
                      "The exported model has no zinc; no atoms or residues were added.",
                      "Training/template overlap cannot be excluded; this is not independent validation.",
                      "Reuse derived AlphaFold data with source attribution under CC BY 4.0; see data/README.md."],
        }
        write_json(staged / "receipt.json", receipt)
        if output_dir.exists() or output_dir.is_symlink():
            raise ValidationError("Export destination appeared during the run; no files replaced")
        staged.rename(output_dir)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--fit-min-plddt", type=float, default=0)
    args = parser.parse_args()
    try:
        receipt = export_bundle(args.data_dir, args.output_dir, args.fit_min_plddt)
    except (ValidationError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.exit(2, f"Export stopped: {error}\n")
    print(f"Exported aligned prediction and audited transform to {args.output_dir}")
