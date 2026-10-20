"""An explicit, narrowly scoped P00918/2CBA structure comparison."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Iterable

import numpy as np

AA3 = dict(zip(
    "ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL".split(),
    "ARNDCQEGHILKMFPSTWYV",
))


class ValidationError(ValueError):
    """Input or mapping does not meet the declared case-study assumptions."""


@dataclass(frozen=True)
class Atom:
    record: str
    name: str
    residue: str
    chain: str
    number: int
    insertion: str
    altloc: str
    xyz: tuple[float, float, float]
    occupancy: float
    b_factor: float
    element: str

    @property
    def residue_key(self):
        return self.number, self.insertion


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inputs(data_dir: Path) -> dict:
    manifest = json.loads((data_dir / "provenance.json").read_text())
    if manifest.get("case") != "P00918 versus 2CBA chain A and AF-P00918-F1 model v6":
        raise ValidationError("Unrecognized input case manifest")
    for item in manifest["files"]:
        path = data_dir / item["path"]
        if path.parent.resolve() != data_dir.resolve():
            raise ValidationError("Input manifest path must be a basename")
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise ValidationError(f"Input fingerprint mismatch: {item['path']}")
    return manifest


def parse_pdb(text: str) -> list[Atom]:
    """Read a single-model PDB; retain alternates for explicit later selection."""
    atoms = []
    model_count = 0
    for line_no, line in enumerate(text.splitlines(), 1):
        kind = line[:6].strip()
        if kind == "MODEL":
            model_count += 1
            if model_count > 1:
                raise ValidationError("Multiple MODEL blocks are unsupported")
        if kind not in {"ATOM", "HETATM"}:
            continue
        if len(line) < 66:
            raise ValidationError(f"Truncated PDB atom line {line_no}")
        try:
            xyz = tuple(float(line[start:start+8]) for start in (30, 38, 46))
            occupancy = float(line[54:60])
            b_factor = float(line[60:66])
            atom = Atom(kind, line[12:16].strip(), line[17:20].strip(), line[21],
                        int(line[22:26]), line[26].strip(), line[16].strip(), xyz,
                        occupancy, b_factor, line[76:78].strip() if len(line) >= 78 else "")
        except ValueError as error:
            raise ValidationError(f"Invalid numeric PDB field on line {line_no}") from error
        if not all(np.isfinite(value) for value in (*xyz, occupancy, b_factor)):
            raise ValidationError(f"Nonfinite PDB field on line {line_no}")
        if not 0 <= occupancy <= 1 or b_factor < 0:
            raise ValidationError(f"Unsupported occupancy/B-factor on line {line_no}")
        atoms.append(atom)
    if not atoms:
        raise ValidationError("PDB contains no coordinate atoms")
    return atoms


def select_atoms(atoms: Iterable[Atom], chain: str, record: str = "ATOM") -> dict:
    """Select highest occupancy; ties prefer blank then A then alphabetically."""
    selected, seen = {}, set()
    for atom in atoms:
        if atom.chain != chain or atom.record != record:
            continue
        key = (atom.number, atom.insertion, atom.name)
        exact = (*key, atom.altloc)
        if exact in seen:
            raise ValidationError(f"Duplicate atom/alternate identifier: {exact}")
        seen.add(exact)
        current = selected.get(key)
        rank = lambda a: (-a.occupancy, 0 if not a.altloc else 1 if a.altloc == "A" else 2, a.altloc)
        if current is None or rank(atom) < rank(current):
            selected[key] = atom
    return selected


def author_key(token: str) -> tuple[int, str]:
    match = re.fullmatch(r"(-?\d+)([A-Za-z]?)", token)
    if not match:
        raise ValidationError(f"Unsupported author residue identifier: {token!r}")
    return int(match[1]), match[2]


def residue_mapping(entity: dict, instance: dict, reference: str) -> dict:
    """Compose author→entity and SIFTS entity→UniProt mappings, verifying letters."""
    sequence = "".join(entity["entity_poly"]["pdbx_seq_one_letter_code_can"].split())
    identifiers = instance["rcsb_polymer_entity_instance_container_identifiers"]
    if identifiers["auth_asym_id"] != "A" or identifiers["entity_id"] != "1":
        raise ValidationError("Unexpected experimental chain/entity")
    authors = identifiers["auth_to_entity_poly_seq_mapping"]
    if len(authors) != len(sequence) or len(set(authors)) != len(authors):
        raise ValidationError("Author/entity map is incomplete or ambiguous")
    alignments = [a for a in entity["rcsb_polymer_entity_align"]
                  if a["reference_database_accession"] == "P00918" and a["reference_database_name"] == "UniProt"]
    if len(alignments) != 1 or alignments[0]["provenance_source"] != "SIFTS":
        raise ValidationError("Expected one SIFTS alignment to P00918")
    mapping, used_reference = {}, set()
    for region in alignments[0]["aligned_regions"]:
        start_entity, start_ref, length = (region[k] for k in ("entity_beg_seq_id", "ref_beg_seq_id", "length"))
        if min(start_entity, start_ref, length) < 1:
            raise ValidationError("Invalid SIFTS interval")
        for offset in range(length):
            e, r = start_entity + offset, start_ref + offset
            if e > len(sequence) or r > len(reference):
                raise ValidationError("SIFTS mapping outside sequence bounds")
            key = author_key(authors[e-1])
            if key in mapping or r in used_reference:
                raise ValidationError("Overlapping SIFTS intervals")
            if sequence[e-1] != reference[r-1]:
                raise ValidationError(f"Mapped sequence mismatch at UniProt {r}")
            mapping[key] = {"entity_position": e, "uniprot_position": r, "amino_acid": reference[r-1]}
            used_reference.add(r)
    return mapping


def kabsch(mobile: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Proper least-squares rigid fit for row-vector coordinate arrays."""
    x, y = np.asarray(mobile, dtype=float), np.asarray(target, dtype=float)
    if x.shape != y.shape or x.ndim != 2 or x.shape[1] != 3 or x.shape[0] < 3:
        raise ValidationError("Rigid fit requires matched N×3 arrays with at least three points")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValidationError("Rigid fit coordinates must be finite")
    cx, cy = x.mean(axis=0), y.mean(axis=0)
    if np.linalg.matrix_rank(x-cx) < 2 or np.linalg.matrix_rank(y-cy) < 2:
        raise ValidationError("Rigid fit points are collinear or coincident")
    u, _, vt = np.linalg.svd((x-cx).T @ (y-cy))
    if np.linalg.det(u @ vt) < 0:
        u[:, -1] *= -1
    rotation = u @ vt
    translation = cy - cx @ rotation
    return x @ rotation + translation, rotation, translation


def rmsd(x, y) -> float:
    return float(np.sqrt(np.mean(np.sum((np.asarray(x) - np.asarray(y)) ** 2, axis=1))))


def comparison(data_dir: Path, fit_min_plddt: float = 0.0) -> dict:
    if not np.isfinite(fit_min_plddt) or not 0 <= fit_min_plddt <= 100:
        raise ValidationError("fit_min_plddt must be between 0 and 100")
    manifest = verify_inputs(data_dir)
    load = lambda name: json.loads((data_dir / name).read_text())
    uniprot, af = load("uniprot_P00918.json"), load("alphafold_P00918.json")[0]
    reference = uniprot["sequence"]["value"]
    if uniprot["primaryAccession"] != "P00918" or af["uniprotAccession"] != "P00918":
        raise ValidationError("Expected P00918 metadata")
    if af["sequence"] != reference or af["latestVersion"] != 6 or af["sequenceStart"] != 1:
        raise ValidationError("Prediction metadata does not match the pinned reference/version")
    entity, instance, entry = load("2cba_polymer_entity_1.json"), load("2cba_chain_A.json"), load("2cba_entry.json")
    if entity["entity_poly"]["rcsb_mutation_count"] != 0:
        raise ValidationError("Experimental metadata reports a mutation")
    mapping = residue_mapping(entity, instance, reference)
    experimental_atoms = parse_pdb((data_dir / "2cba.pdb").read_text())
    predicted_atoms = parse_pdb((data_dir / "AF-P00918-F1-model_v6.pdb").read_text())
    experimental = select_atoms(experimental_atoms, "A")
    predicted = select_atoms(predicted_atoms, "A")
    exp_ca = {mapping[(n, ins)]["uniprot_position"]: atom for (n, ins, name), atom in experimental.items()
              if name == "CA" and (n, ins) in mapping}
    all_exp_ca = [atom for atom in experimental.values() if atom.name == "CA"]
    if len(exp_ca) != len(all_exp_ca):
        raise ValidationError("An experimental Cα has no SIFTS mapping")
    for atom in all_exp_ca:
        item = mapping[atom.residue_key]
        if AA3.get(atom.residue) != item["amino_acid"]:
            raise ValidationError(f"Experimental residue identity mismatch at {atom.residue_key}")
    pred_ca = {n: atom for (n, ins, name), atom in predicted.items() if name == "CA" and not ins}
    if set(pred_ca) != set(range(1, len(reference)+1)):
        raise ValidationError("Prediction must provide exactly one Cα for every canonical residue")
    for pos, atom in pred_ca.items():
        if AA3.get(atom.residue) != reference[pos-1]:
            raise ValidationError(f"Predicted residue identity mismatch at {pos}")
    confidence = load("AF-P00918-F1-confidence_v6.json")
    if confidence["residueNumber"] != list(range(1, len(reference)+1)):
        raise ValidationError("Confidence positions do not match canonical sequence")
    scores = np.asarray(confidence["confidenceScore"], dtype=float)
    if scores.shape != (len(reference),) or not np.isfinite(scores).all() or ((scores < 0) | (scores > 100)).any():
        raise ValidationError("Invalid pLDDT vector")
    if not all(abs(atom.b_factor - scores[pos-1]) <= .011 for pos, atom in pred_ca.items()):
        raise ValidationError("AF coordinate B column does not match its pLDDT sidecar")
    positions = sorted(exp_ca)
    x = np.array([pred_ca[pos].xyz for pos in positions])
    y = np.array([exp_ca[pos].xyz for pos in positions])
    mask = np.array([scores[pos-1] >= fit_min_plddt for pos in positions])
    _, rotation, translation = kabsch(x[mask], y[mask])
    aligned = x @ rotation + translation
    distances = np.linalg.norm(aligned-y, axis=1)
    by_position = {pos: index for index, pos in enumerate(positions)}
    ref_to_mapping = {item["uniprot_position"]: (author, item) for author, item in mapping.items()}
    rows = []
    for pos, aa in enumerate(reference, 1):
        author, mapped = ref_to_mapping.get(pos, (None, None))
        experimental_atom = exp_ca.get(pos)
        idx = by_position.get(pos)
        rows.append({
            "uniprot_position": pos, "amino_acid": aa,
            "entity_position": mapped["entity_position"] if mapped else None,
            "author_residue": f"{author[0]}{author[1]}" if author else None,
            "experimental_ca_present": experimental_atom is not None,
            "mapping_status": "matched_ca" if experimental_atom else "mapped_no_experimental_ca" if mapped else "not_in_sifts_alignment",
            "predicted_plddt": float(scores[pos-1]),
            "experimental_ca_b_factor_A2": experimental_atom.b_factor if experimental_atom else None,
            "experimental_ca_occupancy": experimental_atom.occupancy if experimental_atom else None,
            "experimental_ca_altloc": experimental_atom.altloc if experimental_atom else None,
            "included_in_fit": bool(mask[idx]) if idx is not None else False,
            "ca_displacement_A": float(distances[idx]) if idx is not None else None,
        })
    sensitivity = []
    for threshold in (0, 70, 90):
        subset = np.array([scores[pos-1] >= threshold for pos in positions])
        _, r, t = kabsch(x[subset], y[subset])
        fitted = x @ r + t
        sensitivity.append({"min_plddt": threshold, "fit_residues": int(subset.sum()),
                            "fit_rmsd_A": rmsd(fitted[subset], y[subset]), "all_matched_rmsd_A": rmsd(fitted, y)})
    zinc = [a for a in experimental_atoms if a.record == "HETATM" and a.residue == "ZN" and a.element == "ZN"]
    if len(zinc) != 1:
        raise ValidationError("Expected one experimentally modeled zinc ion")
    zinc_rows = []
    for neighbor in instance["rcsb_ligand_neighbors"]:
        if neighbor["comp_id"] != "HIS":
            continue
        key = (int(neighbor["auth_seq_id"]), "", neighbor["atom_id"])
        atom = experimental.get(key)
        if atom is None:
            raise ValidationError("Annotated zinc-neighbor atom missing")
        distance = float(np.linalg.norm(np.array(atom.xyz)-np.array(zinc[0].xyz)))
        zinc_rows.append({"uniprot_position": mapping[atom.residue_key]["uniprot_position"],
                          "author_residue": atom.number, "atom": atom.name, "distance_to_zinc_A": distance})
    if len(zinc_rows) != 3:
        raise ValidationError("Expected three annotated histidine zinc-neighbor atoms")
    summary = {
        "case": manifest["case"], "reference_length": len(reference),
        "mapped_entity_residues": len(mapping), "matched_ca_residues": len(positions),
        "fit_min_plddt": fit_min_plddt, "fit_residues": int(mask.sum()),
        "fit_rmsd_A": rmsd(aligned[mask], y[mask]), "all_matched_ca_rmsd_A": rmsd(aligned, y),
        "median_ca_displacement_A": float(np.median(distances)),
        "max_ca_displacement_A": float(distances.max()),
        "max_displacement_uniprot_position": positions[int(distances.argmax())],
        "experimental_ca_missing_uniprot_positions": [pos for pos in range(1, len(reference)+1) if pos not in exp_ca],
        "predicted_mean_plddt": float(scores.mean()),
        "experimental_resolution_A": entry["rcsb_entry_info"]["resolution_combined"][0],
        "experimental_nonwater_ligands": entry["rcsb_entry_info"]["nonpolymer_bound_components"],
        "prediction_heteroatom_count": sum(a.record == "HETATM" for a in predicted_atoms),
        "rotation_determinant": float(np.linalg.det(rotation)),
        "interpretation": "Descriptive comparison of overlapping Cα coordinates after a rigid fit; not independent benchmarking, function validation, binding affinity, or activity measurement.",
    }
    return {"summary": summary, "residues": rows, "fit_sensitivity": sensitivity, "zinc_geometry": sorted(zinc_rows, key=lambda r:r["uniprot_position"]),
            "experimental_xyz": y, "aligned_predicted_xyz": aligned, "matched_positions": positions, "experimental_zinc_xyz": zinc[0].xyz,
            "rotation": rotation, "translation": translation}
