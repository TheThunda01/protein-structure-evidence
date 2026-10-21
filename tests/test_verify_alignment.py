import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from export_alignment import export_bundle
from structure_evidence import ValidationError
from verify_alignment import MAX_FILE_BYTES, verify_bundle
from symlink_support import create_symlink_or_skip

ROOT = Path(__file__).resolve().parents[1]


def rewrite_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def rehash_member(bundle, name):
    receipt = json.loads((bundle / "receipt.json").read_text())
    raw = (bundle / name).read_bytes()
    receipt["derived_files"][name] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    rewrite_json(bundle / "receipt.json", receipt)


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.bundle = self.directory / "bundle"
        shutil.copytree(ROOT / "examples/alignment", self.bundle)

    def tearDown(self):
        self.temporary.cleanup()

    def test_valid_existing_bundle_is_read_only(self):
        before = {p.name: p.read_bytes() for p in self.bundle.iterdir()}
        report = verify_bundle(ROOT / "data", self.bundle)
        self.assertTrue(report["verified"])
        self.assertEqual(report["predicted_atoms"], 2073)
        self.assertEqual(report["fit_residues"], 258)
        self.assertFalse(report["runtime_metadata_authenticated"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.bundle.iterdir()})

    def test_alternative_valid_fit_is_recomputed(self):
        other = self.directory / "cutoff90"
        export_bundle(ROOT / "data", other, 90)
        report = verify_bundle(ROOT / "data", other)
        self.assertEqual(report["fit_residues"], 256)
        self.assertEqual(report["evaluation_residues"], 258)

    def test_modified_coordinate_and_confidence_fail_even_after_rehash(self):
        original = (self.bundle / "aligned_prediction.pdb").read_bytes()
        for start, replacement in [(30, b" 999.000"), (60, b"  1.00")]:
            with self.subTest(start=start):
                lines = original.splitlines(keepends=True)
                index = next(i for i, line in enumerate(lines) if line.startswith(b"ATOM"))
                line = lines[index]
                lines[index] = line[:start] + replacement + line[start+len(replacement):]
                (self.bundle / "aligned_prediction.pdb").write_bytes(b"".join(lines))
                rehash_member(self.bundle, "aligned_prediction.pdb")
                with self.assertRaisesRegex(ValidationError, "Model differs"):
                    verify_bundle(ROOT / "data", self.bundle)

    def test_inconsistent_transform_selection_and_metric_fail_after_rehash(self):
        original = json.loads((self.bundle / "transform.json").read_text())
        cases = [
            lambda value: value["fit_uniprot_positions"].pop(),
            lambda value: value["evaluation_uniprot_positions"].reverse(),
            lambda value: value["rotation"][0].__setitem__(0, -1.0),
            lambda value: value.__setitem__("fit_rmsd_A", 0.1),
            lambda value: value.__setitem__("fit_min_plddt", 90.0),
        ]
        for mutate in cases:
            value = json.loads(json.dumps(original))
            mutate(value)
            rewrite_json(self.bundle / "transform.json", value)
            rehash_member(self.bundle, "transform.json")
            with self.subTest(mutation=mutate), self.assertRaises(ValidationError):
                verify_bundle(ROOT / "data", self.bundle)

    def test_source_manifest_and_source_files_are_pinned(self):
        data = self.directory / "data"
        shutil.copytree(ROOT / "data", data)
        model = data / "AF-P00918-F1-model_v6.pdb"
        model.write_bytes(model.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValidationError, "fingerprint"):
            verify_bundle(data, self.bundle)
        manifest = json.loads((data / "provenance.json").read_text())
        for item in manifest["files"]:
            if item["path"] == model.name:
                item["sha256"] = hashlib.sha256(model.read_bytes()).hexdigest()
        rewrite_json(data / "provenance.json", manifest)
        with self.assertRaisesRegex(ValidationError, "pinned case"):
            verify_bundle(data, self.bundle)

    def test_missing_extra_and_oversized_members_are_rejected(self):
        model = self.bundle / "aligned_prediction.pdb"
        raw = model.read_bytes()
        model.unlink()
        with self.assertRaises(ValidationError):
            verify_bundle(ROOT / "data", self.bundle)
        model.write_bytes(raw)
        extra = self.bundle / "extra.txt"
        extra.write_text("unexpected")
        with self.assertRaisesRegex(ValidationError, "only an optional"):
            verify_bundle(ROOT / "data", self.bundle)
        extra.unlink()
        model.write_bytes(b"x" * (MAX_FILE_BYTES + 1))
        with self.assertRaisesRegex(ValidationError, "2 MiB"):
            verify_bundle(ROOT / "data", self.bundle)

    def test_symlink_member_is_rejected(self):
        model = self.bundle / "aligned_prediction.pdb"
        model.unlink()
        create_symlink_or_skip(self, model, ROOT / "examples/alignment/aligned_prediction.pdb")
        with self.assertRaisesRegex(ValidationError, "regular file"):
            verify_bundle(ROOT / "data", self.bundle)

    def test_strict_json_and_receipt_fingerprints(self):
        path = self.bundle / "receipt.json"
        original = path.read_bytes()
        for raw in [b'{"schema_version":1,"schema_version":1}', b'{"schema_version":NaN}', b'[]']:
            path.write_bytes(raw)
            with self.subTest(raw=raw), self.assertRaises(ValidationError):
                verify_bundle(ROOT / "data", self.bundle)
        for key in ["code_sha256", "source_sha256"]:
            value = json.loads(original)
            name = next(iter(value[key]))
            value[key][name] = "0" * 64
            rewrite_json(path, value)
            with self.subTest(key=key), self.assertRaises(ValidationError):
                verify_bundle(ROOT / "data", self.bundle)

    def test_runtime_is_reported_not_authenticated_and_strict_mode_is_optional(self):
        path = self.bundle / "receipt.json"
        receipt = json.loads(path.read_text())
        receipt["runtime"]["python"] = "0.0.1"
        rewrite_json(path, receipt)
        report = verify_bundle(ROOT / "data", self.bundle)
        self.assertFalse(report["runtime_matches_current"])
        self.assertFalse(report["runtime_metadata_authenticated"])
        with self.assertRaisesRegex(ValidationError, "runtime differs"):
            verify_bundle(ROOT / "data", self.bundle, strict_runtime=True)

    def test_cli_json_success_and_failure_exit(self):
        command = [sys.executable, str(ROOT / "verify_alignment.py"), "--data-dir", str(ROOT / "data"),
                   "--bundle-dir", str(self.bundle), "--json"]
        success = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertTrue(json.loads(success.stdout)["verified"])
        (self.bundle / "transform.json").write_text("bad JSON")
        failure = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(failure.returncode, 2)
        self.assertIn("Verification stopped", failure.stderr)
        self.assertEqual(failure.stdout, "")


if __name__ == "__main__":
    unittest.main()
