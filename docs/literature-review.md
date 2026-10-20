# Rapid evidence review

## Question and scope

What would make this small comparison more useful for someone inspecting the same fit in another program, while keeping residue correspondence, confidence, and evidence limits visible?

The review covers reproducible structure comparison, mapping, and coordinate export. It prioritizes primary publications from 1 January 2022 through 20 October 2026 and official file-format/software documentation. Existing foundational work, including Kabsch's fit and the original AlphaFold method, remains in [references](references.md). This is a bounded rapid review, not a complete systematic review or a new accuracy benchmark.


### Round 2 — same-day verification scope (20 October 2026)

This second scope asks how an exported coordinate bundle can be checked against the pinned source and exact fit selection. It is a new implementation question on the same date, not a later surveillance update. Earlier searches and decisions above are retained; new records are in [search-update-02.json](search-update-02.json).

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


### Round 2 search

The first query, `("protein structure"[Title/Abstract]) AND (reproducibility[Title/Abstract] OR provenance[Title/Abstract])`, returned 31 PubMed records; only the first 10 were screened. A focused `ModelCIF[Title]` query returned 2 records, both retrieved. Both used the 2022-01-01 through 2026-10-20 publication window, `publication_date` order, and a 10-record limit. There were 11 unique titles after overlap, one separately retrieved abstract, and one included primary paper. Its complete PMC text was inspected in two chunks. The remaining 21 records from the broad query were not screened. Python 3.12.15 and wwPDB 3.3 documentation supplied implementation details; no third-party code was copied.

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


### Round 2 source-to-claim-to-code additions

| Source | Type and access | Supported claim | Limit | Implementation consequence |
| --- | --- | --- | --- | --- |
| [Tauriello et al., 2026; PMID 41580068](https://doi.org/10.1016/j.jmb.2026.169658) | Primary ModelCIF update; abstract and complete PMC text | Computed-model interchange benefits from explicit protocols, inputs, outputs and provenance. | The paper describes a broad representation standard; this project does not implement or claim ModelCIF compliance. | Verify source/code fingerprints, fit selections and derived coordinates together, rather than treating a PDB file alone as the analysis record. |
| [Python hashlib](https://docs.python.org/3.12/library/hashlib.html) and [HMAC](https://docs.python.org/3.12/library/hmac.html), 3.12.15 | Official APIs; relevant sections | Byte digests and keyed message authentication are different mechanisms. | These APIs do not authenticate an unsigned repository receipt by themselves. | Hash checks are followed by pinned-source recomputation; authorship and runtime metadata remain unauthenticated. No HMAC/signature added. |
| [Python JSON](https://docs.python.org/3.12/library/json.html), 3.12.15 | Official parser documentation; relevant sections | Parsers expose hooks and require care with untrusted input sizes. | JSON parsing alone does not establish semantic correctness. | Limit each bundle member to 2 MiB; reject duplicate keys and nonfinite values; check exact field sets and value types. |
| [wwPDB coordinate format 3.3](https://www.wwpdb.org/documentation/file-format-content/format33/sect9.html) | Official format; relevant fields revisited | Atom coordinates and other fixed-width fields have distinct meanings. | File-format conformance does not validate protein function or the fitting method. | Regenerate the derived PDB from the verified transform and pinned atoms, retaining identity, occupancy and confidence fields. |

## Changes made

The concrete gap was that a report and image did not expose a reusable fitted coordinate file or the exact transform. `export_alignment.py` now writes the existing predicted model in the experimental frame, along with full-precision rotation/translation, fit/evaluation residue lists, and a hash-linked receipt. The exporter preserves atom identity, occupancy, and pLDDT; marks the file as derived; handles obsolete frame records explicitly; and stops on unsupported coordinate-dependent records or field overflow.

Six added tests cover field preservation, invalid transforms, unsupported records, every exported atom against the transform, deterministic bundles, existing-output protection, source corruption, and CLI failure behavior. There are 26 tests overall. The existing numerical result, source files, and checked-in analysis results are unchanged. A new export example illustrates the additional output.

README organization now follows the common portfolio format. The [practical-use guide](practical-use.md) distinguishes implemented checks, operator responsibilities, and future work.


### Round 2 implementation

Added `verify_alignment.py`, a read-only bundle verification command. It anchors the source manifest to a pinned SHA-256, checks receipt fingerprints, recomputes the selected fit using the existing analysis implementation, compares every transform field and regenerates the derived PDB. Changing both a coordinate/selection and its recorded digest therefore does not bypass the consistency check. The check is independent of bundle claims, not an independent implementation of the fitting algorithm. It reports the three verified file hashes and explicitly marks unsigned runtime metadata as unauthenticated. `--strict-runtime` additionally requires exact version-string agreement.

Nine new tests cover valid alternative cutoffs, co-edited hashes, mismatched selections/metrics, changed source manifests, malformed JSON, member restrictions, runtime behavior and CLI exits. The 35-test suite and existing result reproduction pass. Existing source data, result files, original search log and example export remain unchanged.

## Remaining work

The next priorities are a standalone receipt verifier, round-tripped mmCIF support, and independent loading checks in pinned viewer versions. Each has acceptance criteria in [practical use](practical-use.md). Those capabilities are not implemented or implied by this review.


### Round 2 status

The standalone receipt-verification backlog item is now implemented. Remaining priorities are mmCIF interchange, pinned viewer loading checks, and a genuinely independent fit cross-check. Acceptance criteria are updated in [practical use](practical-use.md#next-improvements).

## Limits of this review

One reviewer screened a small set of narrow searches, with no registered protocol, dual screening, formal risk-of-bias assessment, or exhaustive citation chasing. Title exclusions were not full-text appraisals. One included primary method paper was abstract-only; official source inspection supplied implementation details without substituting for independent evaluation. Search indexing and mutable documentation may change after the recorded date. No accuracy estimate, clinical conclusion, or benefit of the export was measured.



### Round 2 limits

This update screened a bounded first page plus one narrow complete query; it is not a full systematic review. Only one new primary paper was appraised in full. The verifier demonstrates reproducibility of this pinned computation, not an independent structural benchmark. Unsigned consistent re-exports cannot be distinguished from their originals as an authorship matter; matching hashes and fit selections do not establish experimental or biological validity.
