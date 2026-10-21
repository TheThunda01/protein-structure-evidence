import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from analyze import run
from structure_evidence import (Atom, ValidationError, author_key, comparison, kabsch,
                                parse_pdb, residue_mapping, rmsd, select_atoms, verify_inputs)

ROOT = Path(__file__).resolve().parents[1]


def atom_line(number=1, altloc="", occupancy=1.0, x=1.0, atom="CA", residue="ALA", insertion=""):
    return f"ATOM  {1:5d} {atom:^4}{altloc:1}{residue:>3} A{number:4d}{insertion:1}   {x:8.3f}{2.0:8.3f}{3.0:8.3f}{occupancy:6.2f}{10.0:6.2f}          {'C':>2}  "


class PdbTests(unittest.TestCase):
    def test_parse_numbering_and_insertion(self):
        atom = parse_pdb(atom_line(number=-2, insertion="A"))[0]
        self.assertEqual(atom.residue_key, (-2, "A"))
        self.assertEqual(atom.xyz, (1.0, 2.0, 3.0))

    def test_alternate_selection_and_tie_policy(self):
        atoms = parse_pdb("\n".join([atom_line(altloc="A", occupancy=.4, x=2), atom_line(altloc="B", occupancy=.6, x=3)]))
        self.assertEqual(select_atoms(atoms, "A")[(1,"","CA")].altloc, "B")
        atoms = parse_pdb("\n".join([atom_line(altloc="A", occupancy=.5), atom_line(altloc="", occupancy=.5)]))
        self.assertEqual(select_atoms(atoms, "A")[(1,"","CA")].altloc, "")

    def test_duplicate_exact_atom_rejected(self):
        with self.assertRaisesRegex(ValidationError, "Duplicate"):
            select_atoms(parse_pdb(atom_line()+"\n"+atom_line()), "A")

    def test_invalid_coordinate_inputs(self):
        for text in ["", "ATOM      1", atom_line(x=float("nan")), atom_line(occupancy=1.1), "MODEL        1\n"+atom_line()+"\nENDMDL\nMODEL        2\n"+atom_line()]:
            with self.subTest(text=text), self.assertRaises(ValidationError):
                parse_pdb(text)

    def test_author_identifiers_are_not_list_offsets(self):
        self.assertEqual(author_key("127"),(127,""))
        self.assertEqual(author_key("42B"),(42,"B"))
        with self.assertRaises(ValidationError):
            author_key("unknown")


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.points = np.array([[0,0,0],[1,0,0],[0,2,0],[0,0,3]],dtype=float)

    def test_known_rigid_transform(self):
        rotation = np.array([[0,-1,0],[1,0,0],[0,0,1]],dtype=float)
        target = self.points @ rotation + [4,-2,9]
        aligned, fitted_rotation, _ = kabsch(self.points,target)
        np.testing.assert_allclose(aligned,target,atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(fitted_rotation),1)
        self.assertAlmostEqual(rmsd(aligned,target),0)

    def test_reflection_is_not_accepted_as_rotation(self):
        target = self.points * [-1,1,1]
        aligned, rotation, _ = kabsch(self.points,target)
        self.assertAlmostEqual(np.linalg.det(rotation),1)
        self.assertGreater(rmsd(aligned,target),0.1)

    def test_degenerate_or_invalid_geometry(self):
        for x,y in [(self.points[:2],self.points[:2]), (self.points,self.points[:3]), (np.zeros((3,3)),np.zeros((3,3))), (self.points*np.nan,self.points)]:
            with self.subTest(x=x), self.assertRaises(ValidationError):
                kabsch(x,y)


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.entity = {"entity_poly":{"pdbx_seq_one_letter_code_can":"XACD"},
                       "rcsb_polymer_entity_align":[{"reference_database_accession":"P00918","reference_database_name":"UniProt","provenance_source":"SIFTS","aligned_regions":[{"entity_beg_seq_id":2,"ref_beg_seq_id":2,"length":3}]}]}
        self.instance = {"rcsb_polymer_entity_instance_container_identifiers":{"auth_asym_id":"A","entity_id":"1","auth_to_entity_poly_seq_mapping":["1","2","4","5"]}}

    def test_gap_in_author_numbers_does_not_become_sequence_gap(self):
        mapped=residue_mapping(self.entity,self.instance,"MACD")
        self.assertEqual(mapped[(4,"")]["uniprot_position"],3)
        self.assertNotIn((1,""),mapped)

    def test_mismatch_overlap_bounds_and_duplicate_author_rejected(self):
        with self.assertRaisesRegex(ValidationError,"sequence mismatch"):
            residue_mapping(self.entity,self.instance,"MAYD")
        bad=copy.deepcopy(self.entity)
        bad["rcsb_polymer_entity_align"][0]["aligned_regions"] *=2
        with self.assertRaisesRegex(ValidationError,"Overlapping"):
            residue_mapping(bad,self.instance,"MACD")
        bad=copy.deepcopy(self.entity)
        bad["rcsb_polymer_entity_align"][0]["aligned_regions"][0]["length"]=5
        with self.assertRaisesRegex(ValidationError,"bounds"):
            residue_mapping(bad,self.instance,"MACD")
        bad=copy.deepcopy(self.instance)
        bad["rcsb_polymer_entity_instance_container_identifiers"]["auth_to_entity_poly_seq_mapping"][2]="2"
        with self.assertRaisesRegex(ValidationError,"ambiguous"):
            residue_mapping(self.entity,bad,"MACD")


class RealSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=comparison(ROOT / "data")

    def test_fixed_snapshot_provenance(self):
        manifest=verify_inputs(ROOT/"data")
        self.assertEqual(len(manifest["files"]),8)
        self.assertEqual(self.result["summary"]["matched_ca_residues"],258)
        self.assertEqual(self.result["summary"]["mapped_entity_residues"],259)

    def test_missing_terminal_state_and_author_gap(self):
        rows=self.result["residues"]
        self.assertEqual(rows[0]["mapping_status"],"not_in_sifts_alignment")
        self.assertEqual(rows[1]["mapping_status"],"mapped_no_experimental_ca")
        self.assertEqual(rows[125]["author_residue"],"127")
        self.assertTrue(rows[125]["experimental_ca_present"])
        self.assertEqual(rows[-1]["author_residue"],"261")

    def test_pinned_numerical_result(self):
        s=self.result["summary"]
        self.assertAlmostEqual(s["all_matched_ca_rmsd_A"],0.5312317195,places=8)
        self.assertEqual(s["max_displacement_uniprot_position"],3)
        self.assertEqual(s["experimental_nonwater_ligands"],["ZN"])
        self.assertEqual(s["prediction_heteroatom_count"],0)

    def test_zinc_distances_use_documented_atoms(self):
        rows=self.result["zinc_geometry"]
        self.assertEqual([(r["uniprot_position"],r["atom"]) for r in rows],[(94,"NE2"),(96,"NE2"),(119,"ND1")])
        for row in rows:
            self.assertTrue(2.0 < row["distance_to_zinc_A"] < 2.2)

    def test_fit_selection_is_explicit_and_can_be_infeasible(self):
        other=comparison(ROOT/"data",90)
        self.assertEqual(other["summary"]["fit_residues"],256)
        for value in [-1,101,float("nan"),100]:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                comparison(ROOT/"data",value)

    def test_corrupted_input_is_rejected_before_analysis(self):
        with tempfile.TemporaryDirectory() as temp:
            data=Path(temp)/"data"
            shutil.copytree(ROOT/"data",data)
            with (data/"2cba.pdb").open("a") as handle:
                handle.write("\nchanged\n")
            with self.assertRaisesRegex(ValidationError,"fingerprint"):
                comparison(data)

    def test_confidence_column_cannot_be_silently_reinterpreted(self):
        with tempfile.TemporaryDirectory() as temp:
            data=Path(temp)/"data"
            shutil.copytree(ROOT/"data",data)
            path=data/"AF-P00918-F1-confidence_v6.json"
            values=json.loads(path.read_text())
            values["confidenceScore"][10]=20
            path.write_text(json.dumps(values))
            # Bypass only the fingerprint guard to test the independent semantic guard.
            with patch("structure_evidence.verify_inputs",return_value=verify_inputs(ROOT/"data")):
                with self.assertRaisesRegex(ValidationError,"does not match its pLDDT"):
                    comparison(data)

    def test_prediction_sequence_must_match_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            data=Path(temp)/"data"
            shutil.copytree(ROOT/"data",data)
            path=data/"alphafold_P00918.json"
            values=json.loads(path.read_text())
            values[0]["sequence"]="A"+values[0]["sequence"][1:]
            path.write_text(json.dumps(values))
            with patch("structure_evidence.verify_inputs",return_value=verify_inputs(ROOT/"data")):
                with self.assertRaisesRegex(ValidationError,"does not match the pinned"):
                    comparison(data)

    def test_reproducible_json_and_source_preservation(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"results"
            first=run(ROOT/"data",out,make_figures=False)
            before={p.name:p.read_bytes() for p in out.iterdir()}
            second=run(ROOT/"data",out,make_figures=False)
            self.assertEqual(first,second)
            self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})
            verify_inputs(ROOT/"data")
            self.assertFalse(first["plots_generated"])

    def test_no_plots_does_not_leave_stale_figures(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            (out/"evidence_profiles.png").write_bytes(b"old image")
            (out/"backbone_overlay.png").write_bytes(b"old image")
            run(ROOT/"data",out,make_figures=False)
            self.assertFalse((out/"evidence_profiles.png").exists())
            self.assertFalse((out/"backbone_overlay.png").exists())

    def test_cli_completes_with_legacy_windows_stdout_encoding(self):
        with tempfile.TemporaryDirectory() as temp:
            process = subprocess.run(
                [sys.executable, str(ROOT/"analyze.py"), "--data-dir", str(ROOT/"data"),
                 "--output-dir", temp, "--no-plots"],
                env=dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0"),
                capture_output=True,
            )
            self.assertEqual(process.returncode, 0, process.stderr.decode("cp1252", errors="replace"))
            self.assertIn(b"Compared 258 C-alpha pairs", process.stdout)
            self.assertTrue((Path(temp)/"summary.json").is_file())


if __name__ == "__main__":
    unittest.main()
