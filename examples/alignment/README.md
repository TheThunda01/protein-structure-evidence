# Default alignment export

Generated offline with `python export_alignment.py --output-dir examples/alignment` using the pinned source snapshots and all 258 comparable Cα positions. This directory contains a derived AlphaFold coordinate file, its full-precision rigid transform, and an integrity receipt. The export command requires a new destination; use another directory to reproduce it without deleting this example.

The RMSD of the original, full-precision fit is 0.5312317195 Å. Saved PDB coordinates are rounded to three decimals. Predicted pLDDT and occupancy are unchanged, all 260 predicted residues remain, and no zinc or experimental coordinates have been inserted. Placeholder crystal/frame records have been removed. The [practical-use guide](../../docs/practical-use.md) documents exact fields and limitations.

These are derived data for visual inspection, not new predictions or experimental evidence. The historical comparison may overlap training/templates and is not an independent benchmark. Retain the [AlphaFold data attribution and CC BY 4.0 terms](../../data/README.md).
