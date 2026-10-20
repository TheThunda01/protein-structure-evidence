# Protein Structure Evidence

**How much does a predicted protein structure tell us when we also have an experimental model?** This worked example compares human carbonic anhydrase II using explicit residue mapping, a reproducible backbone fit, and separate displays of confidence and experimental displacement parameters.

Start with the [biology and concepts](docs/biology-and-concepts.md), then see [methods and limits](docs/methods.md). This is a completed educational case study, version 0.1.0, developed with AI assistance and checked with executable examples. It is not a new structure determination or a functional validation study.

For a quick overview, read [project context: background, purpose, and main themes](docs/project-context.md).

## The case

| Source | Selected evidence |
| --- | --- |
| [UniProt P00918](https://www.uniprot.org/uniprotkb/P00918/entry) | Canonical human CAII sequence, 260 residues; sequence version 2. |
| [PDB 2CBA](https://www.rcsb.org/structure/2CBA) | Chain A, X-ray model at 1.54 Å; no reported amino-acid mutations; zinc is the only nonwater ligand. |
| [AlphaFold DB P00918](https://alphafold.ebi.ac.uk/entry/P00918) | Pinned `AF-P00918-F1-model_v6`, generated 1 August 2025 by the AlphaFold Monomer v2.0 pipeline. |

The experimental structure has a chemically modified N terminus, whereas the prediction represents the canonical sequence. The analysis checks these differences rather than assuming that matching protein names guarantee identical inputs.

**Training or template overlap cannot be excluded.** 2CBA predates AlphaFold training. This comparison is a descriptive illustration, not an independent test of AlphaFold generalization. A small fitted RMSD does not validate the prediction method or prove biological function.

## Run it

Use Python 3.12 from the repository root:

```sh
python -m pip install -r requirements.txt
python analyze.py
python -m unittest discover -s tests -v
```

All source snapshots are included, so analysis runs offline after dependencies are installed. `make demo` and `make test` are equivalent shortcuts. The optional [source retrieval script](scripts/fetch_data.py) downloads the same inputs only if their fingerprints still match the recorded snapshot.

## What the run produces

| Output | Purpose |
| --- | --- |
| [Report](results/report.md) / [summary JSON](results/summary.json) | Main counts, fit settings, and descriptive results. |
| [Residue comparison](results/residue_comparison.csv) | All 260 canonical positions, numbering correspondence, missing Cα values, pLDDT, experimental Cα B factors, and fitted displacements. |
| [Fit sensitivity](results/fit_sensitivity.csv) | Fixed pLDDT inclusion cutoffs of 0, 70, and 90, with separate fitting and evaluation denominators. |
| [Zinc geometry](results/zinc_geometry.csv) | Three experimental Zn–histidine atom distances. No zinc is inserted into the prediction. |
| [Evidence profiles](results/evidence_profiles.png) / [backbone overlay](results/backbone_overlay.png) | Separate evidence panels and a matched Cα trace comparison. |

The default run fits all **258 matched Cα pairs**, giving an RMSD of **0.531 Å**. The largest displacement is **6.499 Å** at canonical residue **3**. This terminal residue also has pLDDT **69.06** and experimental Cα occupancy **0.50**. Those observations are worth inspecting together, but this analysis cannot determine the cause of their disagreement.

![Separate confidence, displacement, and experimental B-factor profiles](results/evidence_profiles.png)

## Why mapping matters here

Canonical positions 1–2 have no comparable experimental Cα coordinates. The PDB declares an ACE cap at entity position 1 instead of canonical Met1, and Ser2 is unmodeled. A different issue occurs later: author residue numbers jump from 125 to 127, while canonical numbering remains continuous. Author 127 maps to UniProt 126. Treating the absent author number as a missing amino acid would misalign the rest of the chain.

The code composes RCSB author-to-entity mapping with its SIFTS entity-to-UniProt alignment, then verifies amino-acid identity at every compared Cα. It also checks the prediction's sequence and cross-checks its coordinate-file confidence values against the separate AlphaFold confidence file.

## Interpretation boundaries

- pLDDT is predicted local confidence. An experimental B factor is a different quantity with different units; their shared PDB storage column does not make them comparable scores.
- RMSD depends on the mapped atoms and fitted subset. The sensitivity table keeps those selections visible, and changing a cutoff is not evidence of better prediction accuracy.
- A Cα comparison does not validate side-chain placement, waters, dynamics, catalytic activity, or binding affinity.
- The crystal contains zinc; this AlphaFold monomer file does not. Missing predicted cofactors are not evidence that the biological protein lacks them.

Code is MIT licensed. Source data retain their respective [reuse conditions and attribution](data/README.md). Full scientific references are in [references](docs/references.md).
