import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np

from export_alignment import export_bundle, transform_pdb
from structure_evidence import ValidationError, parse_pdb, sha256
from test_structure_evidence import atom_line

ROOT = Path(__file__).resolve().parents[1]


class ExportTests(unittest.TestCase):
    def test_transform_preserves_atom_fields_and_removes_old_frame(self):
        line = atom_line(altloc="A", occupancy=.5)
        text = "HEADER    TEST\nTITLE     ORIGINAL MODEL\nCRYST1    old frame\nORIGX1    old frame\nSCALE1    old frame\n" + line + "\nEND\n"
        exported, removed = transform_pdb(text, np.eye(3), np.array([1., 2., 3.]))
        new_line = next(x for x in exported.splitlines() if x.startswith("ATOM"))
        self.assertEqual(new_line[:30], line[:30])
        self.assertEqual(new_line[54:], line[54:])
        self.assertEqual(parse_pdb(exported)[0].xyz, (2., 4., 6.))
        self.assertEqual(removed, ["CRYST1", "ORIGX1", "SCALE1"])
        self.assertNotIn("old frame", exported)
        self.assertLess(exported.index("TITLE"), exported.index("REMARK 900"))
        self.assertLess(exported.index("REMARK 900"), exported.index("ATOM"))

    def test_unsafe_transforms_and_coordinate_overflow_fail(self):
        for rotation, translation in [(np.diag([-1., 1., 1.]), np.zeros(3)),
                                      (2*np.eye(3), np.zeros(3)),
                                      (np.eye(3), np.array([np.nan, 0., 0.])),
                                      (np.eye(3), np.array([100000., 0., 0.]))]:
            with self.subTest(rotation=rotation), self.assertRaises(ValidationError):
                transform_pdb(atom_line(), rotation, translation)

    def test_unsupported_coordinate_dependent_records_fail(self):
        for kind in ["ANISOU", "SIGATM", "SIGUIJ", "MTRIX1"]:
            with self.subTest(kind=kind), self.assertRaisesRegex(ValidationError, "does not transform"):
                transform_pdb(atom_line()+"\n"+kind+"\n", np.eye(3), np.zeros(3))

    def test_real_export_matches_unrounded_transform_and_checksums(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)/"bundle"
            before = {p.name: sha256(p) for p in (ROOT/"data").iterdir() if p.is_file()}
            receipt = export_bundle(ROOT/"data", out, 90)
            transform = json.loads((out/"transform.json").read_text())
            original = parse_pdb((ROOT/"data/AF-P00918-F1-model_v6.pdb").read_text())
            exported = parse_pdb((out/"aligned_prediction.pdb").read_text())
            self.assertEqual(len(original), len(exported))
            expected = np.array([a.xyz for a in original]) @ np.array(transform["rotation"]) + transform["translation"]
            np.testing.assert_allclose([a.xyz for a in exported], expected, atol=.000501, rtol=0)
            self.assertEqual([a.b_factor for a in original], [a.b_factor for a in exported])
            self.assertEqual([a.occupancy for a in original], [a.occupancy for a in exported])
            self.assertEqual(len(transform["fit_uniprot_positions"]), 256)
            self.assertEqual(len(transform["evaluation_uniprot_positions"]), 258)
            for name, entry in receipt["derived_files"].items():
                self.assertEqual(sha256(out/name), entry["sha256"])
                self.assertEqual((out/name).stat().st_size, entry["bytes"])
            self.assertEqual(before, {p.name: sha256(p) for p in (ROOT/"data").iterdir() if p.is_file()})

    def test_reproducible_bundle_and_existing_destination_protected(self):
        with tempfile.TemporaryDirectory() as temp:
            first, second = Path(temp)/"first", Path(temp)/"second"
            export_bundle(ROOT/"data", first)
            export_bundle(ROOT/"data", second)
            files = {p.name: p.read_bytes() for p in first.iterdir()}
            self.assertEqual(files, {p.name: p.read_bytes() for p in second.iterdir()})
            with self.assertRaisesRegex(ValidationError, "already exists"):
                export_bundle(ROOT/"data", first)
            self.assertEqual(files, {p.name: p.read_bytes() for p in first.iterdir()})
            with self.assertRaisesRegex(ValidationError, "outside source"):
                export_bundle(ROOT/"data", ROOT/"data/new-output")
            link = Path(temp)/"broken-link"
            link.symlink_to(Path(temp)/"absent-target", target_is_directory=True)
            with self.assertRaisesRegex(ValidationError, "already exists"):
                export_bundle(ROOT/"data", link)
            self.assertTrue(link.is_symlink())

    def test_corruption_fails_without_partial_bundle_and_cli_exit_is_two(self):
        with tempfile.TemporaryDirectory() as temp:
            data, out = Path(temp)/"data", Path(temp)/"out"
            shutil.copytree(ROOT/"data", data)
            with (data/"2cba.pdb").open("a") as handle:
                handle.write("changed\n")
            process = subprocess.run([sys.executable, str(ROOT/"export_alignment.py"),
                                      "--data-dir", str(data), "--output-dir", str(out)],
                                     text=True, capture_output=True)
            self.assertEqual(process.returncode, 2)
            self.assertIn("fingerprint", process.stderr)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
