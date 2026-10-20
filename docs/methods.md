# Methods and limitations

For the new aligned-coordinate export, see the [input/output contract and failure behavior](practical-use.md). The [rapid review](literature-review.md) records the evidence and software inspection behind that addition. Exporting applies the already computed proper rigid transform to all predicted atoms and does not change the fit, the baseline results, or their scientific interpretation.

The round-2 `verify_alignment.py` command additionally checks a bundle against an anchored source-manifest hash and a recomputed fit, then regenerates every exported atom. It uses the existing fitter, so this is a reproducibility check rather than independent algorithm validation. Its exact schema, tolerance, metadata boundaries and failure behavior are in the [practical-use contract](practical-use.md#input-and-output-contract). The [separate search update](search-update-02.json) preserves the original review log.

## Fixed inputs, not an unrestricted structure matcher

This analysis is deliberately specific to UniProt P00918, experimental 2CBA chain A, and AlphaFold DB model v6. Every source file is fingerprinted in `data/provenance.json`; analysis stops if a byte differs. JSON API snapshots were serialized with `json.dumps(parsed_json, indent=2)`; coordinate files and the AlphaFold confidence sidecar retain their downloaded bytes. A checksum establishes file identity, not scientific accuracy.

The PDB entry belongs to a publication describing several chemical states. The selected entry contains zinc and no reported amino-acid mutations. It still differs chemically from the prediction: its deposited polymer sequence begins with an ACE group where the canonical sequence has Met1. “No reported mutation” is not “identical chemical state.”

## Residue correspondence

RCSB supplies an author-to-polymer-entity mapping for chain A and a SIFTS alignment from polymer entity positions to UniProt. The code composes them; it does not infer canonical position from a PDB author number. Overlapping or out-of-bounds mappings, duplicate author identifiers, and sequence mismatches fail. Observed Cα identities must match the canonical amino acids.

In this snapshot, SIFTS maps entity 2–260 to canonical 2–260. ACE1 is outside that alignment; Ser2 has no observed Cα. There are 258 matched Cα pairs. The author numbering jump after 125 is a labeling gap: author 127 is canonical 126. These distinctions are why missing coordinates and numbering gaps are reported separately. See [RCSB's numbering guide](https://www.rcsb.org/docs/general-help/identifiers-in-pdb) and the [SIFTS methods paper](https://doi.org/10.1038/s41597-023-02101-6).

## Atom choice and rigid fitting

The parser accepts single-model PDB snapshots. It retains chain A protein atoms, rejects duplicate atom/alternate keys and nonfinite coordinates, and selects the highest-occupancy alternate when alternatives exist. Occupancy ties prefer a blank alternate label, then A, then alphabetical order. Occupancy and selected alternate labels are retained for each experimental Cα.

A proper least-squares rotation and translation align predicted to experimental Cα coordinates. The NumPy SVD implementation enforces determinant +1, so a mirror reflection cannot count as a rotation. The default uses every matched Cα with equal weight; experimental occupancy does not weight the fit. Degenerate point sets fail. The calculation follows the rigid-fit problem described by [Kabsch (1976)](https://doi.org/10.1107/S0567739476001873).

Per-residue displacement is Euclidean distance after that fit. RMSD is the square root of the mean squared displacement. The fixed sensitivity analyses fit positions with pLDDT ≥0, ≥70, or ≥90, then report both fit-set RMSD and RMSD over all 258 matched positions. This shows selection sensitivity; it does not justify choosing the lowest number after seeing the results. `--fit-min-plddt` records an alternative primary fit threshold explicitly.

## Confidence and chemical context

The AlphaFold confidence sidecar must cover the full canonical sequence, remain within 0–100, and match the prediction's Cα B-column values within rounding tolerance. Those values are labeled pLDDT. Experimental Cα B values are separately labeled in Å², never converted into pLDDT or combined with it. No predicted aligned error analysis is performed.

For context, experimental zinc distances are calculated to the three histidine donor atoms listed in the RCSB neighbor annotation: His94 NE2, His96 NE2, and His119 ND1. These are coordinate distances, not inferred bond energies or measurements of catalytic activity. The prediction has no heteroatoms; no cofactor is added or transferred from the crystal.

## Limits of the comparison

2CBA is a historical structure. Training or template overlap with AlphaFold cannot be excluded, so this is not an independent generalization benchmark. Fitted differences also mix prediction behavior, chemical-state differences, experimental environment and model uncertainty. Their causes are not identifiable here. The calculation does not test side-chain accuracy, dynamics, protonation, activity, affinity, clinical relevance, or a proposed mechanism.

The figures are generated with Matplotlib. Numerical outputs are rounded to six decimal places for readable tables; fitting uses unrounded coordinates. Tests cover rigid transformations/reflections, mapping/numbering errors, alternate atoms, missing positions, checksums, fixed numerical results, and deterministic tabular output.
