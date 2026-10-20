# Rapid evidence review

## Question and scope

What would make this small comparison more useful for someone inspecting the same fit in another program, while keeping residue correspondence, confidence, and evidence limits visible?

The review covers reproducible structure comparison, mapping, and coordinate export. It prioritizes primary publications from 1 January 2022 through 20 October 2026 and official file-format/software documentation. Existing foundational work, including Kabsch's fit and the original AlphaFold method, remains in [references](references.md). This is a bounded rapid review, not a complete systematic review or a new accuracy benchmark.

## Search record

Searches were executed through the PubMed connector on **20 October 2026**, ordered by `publication_date`, with at most 20 records per call. All publication queries used the date interval above. Exact syntax, IDs, failures, and individual decisions are in the [machine-readable log](search-log.json).

| Search | PubMed query before the common date filter | Total / retrieved | Decision |
| --- | --- | --- | --- |
| P0/P1 | `("AlphaFold"[Title/Abstract]) AND ("local confidence"[Title/Abstract] OR "structural comparison"[Title/Abstract])` | 22 / first 20 in each duplicate execution | P0 was repeated as P1 to retain structured metadata; duplicates counted once. |
| P2 | Same query, offset 20 | 22 / remaining 2 | Completes the broad query. |
| P3 | `SIFTS[Title]` | 1 / 1 | Returned a preprint; not used as peer-reviewed evidence. |
| P4 | `("AlphaFold Protein Structure Database"[Title] OR "US-align"[Title])` | 9 / 9 | Retained the current database update and primary comparison method. |
| P5 | `"Unified access to up-to-date residue-level annotations"[Title]` | 0 / 0 | Did not recover the known mapping paper; retrieved PMID 37045837 directly from the existing verified reference. |

Across successful searches there were **32 distinct records**. Including the seeded mapping paper gives **33 titles screened**. Five PubMed records were separately retrieved for abstract appraisal: 41273079, 36038728, 40604267, 37045837, and 40496892. Three primary papers support the changes: two had complete full text inspected; US-align's primary paper was appraised from its abstract. The SIFTS full text required a second chunk at character offset 20,000. Author-list pagination was not completed where it did not affect screening. These counts describe this search, not the size of the wider literature.

Most broad-query hits concerned individual proteins, pathogens, ligands, or activity experiments outside this question. A nuclear-receptor comparison was considered from its abstract but excluded because its family-specific results cannot establish CAII behavior. The US-align protocol was supplementary context, not primary performance evidence. Official wwPDB pages, EMBL-EBI training material, and pinned US-align source were then inspected. Web result totals were unavailable and are recorded as unknown; the AlphaFold FAQ returned only a rendered shell and was not used for new substantive claims.

## What the sources support

| Source | Type and access | Relevant finding | Limit | Implementation consequence |
| --- | --- | --- | --- | --- |
| [Bertoni et al., PMID 41273079](https://doi.org/10.1093/nar/gkaf1226), 2026 publication | Primary database update; full text | AFDB was updated against UniProt 2025_03 and exposes model/annotation views. | A database update does not validate the accuracy of this comparison or erase possible training overlap. | Keep source version and sequence checks; include their hashes in the export receipt. |
| [Choudhary et al., PMID 37045837](https://doi.org/10.1038/s41597-023-02101-6), 2023 | Primary data-integration paper; complete full text in two chunks | Depositor numbering can differ from protein-sequence numbering; integrated residue annotations improve interoperability. | Mappings remain resource-specific evidence, not proof that all structures have identical chemistry. | Retain explicit author/entity/UniProt mapping; export fit and evaluation position lists rather than just a score. |
| [Zhang et al., PMID 36038728](https://doi.org/10.1038/s41592-022-01585-1), 2022 | Primary structural-alignment method; abstract only | US-align searches structural alignments using a TM-score objective. | Its search objective and scope differ from a fixed-correspondence Cα least-squares fit. No performance claim is transferred here. | Describe this project as a mapped rigid fit; do not label its RMSD or export equivalent to US-align. |
| [US-align source](https://github.com/pylelab/USalign/tree/23f14ffcf8647f2dc1c0e01043db3a7f3a661c28), version 20261019 | Official source/readme/license inspection; commit `23f14ffcf8647f2dc1c0e01043db3a7f3a661c28` | Provides superposition output and matrix/export-related options; reusable transformed coordinates are a practical output. | Not installed or benchmarked here. Its custom permissive notice requires retained notices/references; it is not relabeled as MIT. | Add a small independent exporter and machine-readable transform. No source code was copied. |
| [wwPDB format 3.3, coordinates](https://www.wwpdb.org/documentation/file-format-content/format33/sect9.html) and [transforms](https://www.wwpdb.org/documentation/file-format-content/format33/sect8.html) | Official specification; relevant sections inspected | Cartesian coordinates occupy fixed 8.3 fields in ångströms; anisotropic and frame records carry related quantities. | Legacy PDB is constrained and is not the general archive interchange format. | Check width/overflow, retain atom fields, remove stale frame placeholders, and reject unsupported tensor/transform records. |
| [EMBL-EBI pLDDT guide](https://www.ebi.ac.uk/training/online/courses/alphafold/inputs-and-outputs/evaluating-alphafolds-predicted-structures-using-confidence-scores/plddt-understanding-local-confidence/) | Official training page; full relevant text | pLDDT describes local confidence and does not by itself establish relative domain orientation. | Interpretive guidance is not case-specific calibration or experimental validation. | Preserve confidence values and label them explicitly; do not turn the rigid fit into a confidence or function claim. |

The existing B-factor/pLDDT distinction and training-overlap caveat remain. The review supports better traceability and interchange, not stronger biological conclusions.

## Changes made

The concrete gap was that a report and image did not expose a reusable fitted coordinate file or the exact transform. `export_alignment.py` now writes the existing predicted model in the experimental frame, along with full-precision rotation/translation, fit/evaluation residue lists, and a hash-linked receipt. The exporter preserves atom identity, occupancy, and pLDDT; marks the file as derived; handles obsolete frame records explicitly; and stops on unsupported coordinate-dependent records or field overflow.

Six added tests cover field preservation, invalid transforms, unsupported records, every exported atom against the transform, deterministic bundles, existing-output protection, source corruption, and CLI failure behavior. There are 26 tests overall. The existing numerical result, source files, and checked-in analysis results are unchanged. A new export example illustrates the additional output.

README organization now follows the common portfolio format. The [practical-use guide](practical-use.md) distinguishes implemented checks, operator responsibilities, and future work.

## Remaining work

The next priorities are a standalone receipt verifier, round-tripped mmCIF support, and independent loading checks in pinned viewer versions. Each has acceptance criteria in [practical use](practical-use.md). Those capabilities are not implemented or implied by this review.

## Limits of this review

One reviewer screened a small set of narrow searches, with no registered protocol, dual screening, formal risk-of-bias assessment, or exhaustive citation chasing. Title exclusions were not full-text appraisals. One included primary method paper was abstract-only; official source inspection supplied implementation details without substituting for independent evaluation. Search indexing and mutable documentation may change after the recorded date. No accuracy estimate, clinical conclusion, or benefit of the export was measured.

