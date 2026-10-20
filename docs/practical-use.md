# Practical use

## Where this fits

This repository is a worked example for inspecting an existing predicted structure against one experimentally determined model of the same human protein. It is useful when learning how database numbering, missing coordinates, fitting choices, and confidence affect an overlay. It does not accept arbitrary protein pairs or establish catalytic function.

The implementation now includes a viewer-oriented export. Saving the applied transform and its residue selection makes it possible to inspect the same fitted state elsewhere, rather than reconstructing the alignment by eye. This follows the general importance of interoperable residue mapping described by [Choudhary et al. (2023)](https://doi.org/10.1038/s41597-023-02101-6); the specific export design is an engineering choice here.

## Input and output contract

Both commands accept the pinned `data/` directory. Before calculation, the code verifies its manifest and eight input fingerprints, then checks sequence identity, SIFTS correspondence, atom availability, and prediction confidence. The data are identified as P00918, 2CBA chain A, and AF-P00918-F1 version 6. A changed file, infeasible fit, malformed coordinate field, or inconsistent sequence stops the run.

`analyze.py` produces the documented reports and plots. Its existing outputs and scientific results are unchanged by the export feature.

`export_alignment.py --output-dir NEW_DIRECTORY` writes three files:

| File | Contract |
| --- | --- |
| `aligned_prediction.pdb` | All 2,073 predicted atoms transformed into the experimental Cartesian frame. ATOM/HETATM identity, occupancy, and confidence columns are retained; only coordinate columns change. Derived-file remarks are added. No experimental atoms are merged in. |
| `transform.json` | Schema version 1; full-precision rotation and translation; explicit row-vector equation `aligned = original @ rotation + translation`; coordinates in ångströms; fit and evaluation UniProt position lists; fit cutoff; descriptive RMSDs; removed frame-record names. |
| `receipt.json` | Schema version 1; source-manifest hash and eight source hashes; code hashes; Python/NumPy versions; derived-file byte counts and SHA-256 values; interpretation and reuse notes. |

The optional `--fit-min-plddt` is a number from 0 through 100 and uses the existing fit-selection behavior. At least three noncollinear selected Cα pairs are needed. All mapped pairs remain the evaluation set. Values are not searched for an apparently favorable RMSD.

The export writes a new complete directory and refuses an existing destination or a destination inside source data. Validation failures exit with status 2. It never overwrites source coordinates. It rejects ANISOU, SIGATM, SIGUIJ, and MTRIX records because it does not transform their dependent quantities. It removes CRYST1, SCALE, and ORIGX records from this predicted model rather than carrying an old frame into a new one. The source model's unit cell is a placeholder, not a measured crystal cell. These record meanings and coordinate field widths come from the [wwPDB format specification](https://www.wwpdb.org/documentation/file-format-content/format33/sect8.html) and [coordinate section](https://www.wwpdb.org/documentation/file-format-content/format33/sect9.html).

Coordinates use the PDB 8.3 fields, so saved values differ from full precision by at most 0.0005 Å per component, apart from floating-point tolerance. Coordinate overflow fails. The transform JSON retains full floating-point precision; a viewer's own fit may choose a different subset and produce a different overlay.

## Worked use case

From the repository root, with dependencies installed:

```sh
python analyze.py --output-dir /tmp/caii-review-results
python export_alignment.py --output-dir derived/inspection-001
```

Choose a fresh export directory each time. Open its `aligned_prediction.pdb` alongside `data/2cba.pdb` in a local molecular viewer. Avoid an automatic second alignment if you want to inspect the saved fit. Color predicted confidence and experimental B factors separately. [EMBL-EBI's confidence guide](https://www.ebi.ac.uk/training/online/courses/alphafold/inputs-and-outputs/evaluating-alphafolds-predicted-structures-using-confidence-scores/plddt-understanding-local-confidence/) explains why local confidence does not establish interdomain orientation.

The default export records 258 fitted and evaluated positions and RMSD 0.5312317195 Å. The [checked-in example](../examples/alignment/README.md) contains this state. The transformed file retains all 260 predicted residues, including positions without experimental Cα counterparts; fitting does not make those positions experimentally observed.

## Checks before relying on a result

The code checks input identities and hashes, a proper rotation, available mapped atoms, and file-format limits. Tests also compare every exported atom against the recorded transform and check that its confidence and occupancy are unchanged.

The operator still needs to keep the receipt with the exported model, verify hashes after moving files, inspect which positions entered the fit, and preserve [data attribution](../data/README.md). A receipt detects accidental changes when its recorded hashes are checked; it is not a cryptographic signature or an independent validator. Confirm source versions and chemistry before interpreting a different case outside this repository.

## Known limits

This case may overlap AlphaFold training or templates. It cannot provide an independent accuracy benchmark. The N terminus differs chemically, some experimental coordinates are absent, and only Cα correspondence determines the fit. The comparison does not resolve causes of disagreement or assess activity, binding affinity, conformational populations, or clinical significance. An exported model is a transformed copy, not a refined or newly predicted structure.

The exporter supports this single-chain PDB snapshot, not general mmCIF, assemblies, coordinate uncertainty tensors, or periodic crystallographic calculations. It preserves the original pLDDT values without recalibrating them. Runtime-version changes may alter a receipt even if rounded coordinates are unchanged.

## Next improvements

1. **Receipt verification command:** accept a bundle and its pinned source directory; fail for any altered model, transform, missing file, or inconsistent fit selection. Test each corruption independently.
2. **mmCIF export:** use a maintained parser and preserve author/entity/UniProt identifiers and units; require round-trip tests before accepting inputs beyond this case.
3. **Independent viewer checks:** pin at least two viewer versions and document successful loading plus coordinate agreement without a second fit. No claim of tested viewer compatibility until those checks exist.
4. **More case studies:** add a benign, independently justified structure pair with documented chemistry and evaluation cutoff. Require explicit checks for possible training/template overlap; do not pool RMSDs across unrelated proteins as a performance score.
