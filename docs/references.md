# References and the claims they support

The advancement round's source appraisal and exact search record are in the [rapid literature review](literature-review.md). It includes the current AFDB update, SIFTS mapping paper, US-align comparison, wwPDB file-format specification, and EMBL-EBI confidence guide, with access limits and implementation consequences.

Sources were checked on 20 October 2026. Database records and their downloaded file versions should also be recorded in the analysis provenance. A database's coverage or a method's average performance does not validate an individual protein comparison.

## Biochemical identity and background

1. **UniProtKB P00918, CAH2_HUMAN.** Human carbonic anhydrase 2 identity, canonical sequence, catalytic annotation, and metal-binding features. https://www.uniprot.org/uniprotkb/P00918/entry. The REST record checked for this project listed a 260-residue sequence and an annotation update of 2 September 2026.
2. **McCall KA, Huang C, Fierke CA. (2000).** Function and mechanism of zinc metalloenzymes. *Journal of Nutrition*, 130(5S Suppl), 1437S–1446S. https://doi.org/10.1093/jn/130.5.1437S. An authoritative review used for conceptual metal-enzyme and physiological background, not as evidence of activity in this analysis.
3. **Håkansson K, Carlsson M, Svensson LA, Liljas A. (1992).** Structure of native and apo carbonic anhydrase II and structure of some of its anion-ligand complexes. *Journal of Molecular Biology*, 227(4), 1192–1204. https://doi.org/10.1016/0022-2836(92)90531-n. Primary structural evidence for CAII and its catalytic environment. This reference covers several structures; record-specific experimental details must come from the actual entry selected.

## Prediction method and database

4. **Jumper J et al. (2021).** Highly accurate protein structure prediction with AlphaFold. *Nature*, 596, 583–589. https://doi.org/10.1038/s41586-021-03819-2. Primary AlphaFold2 method and assessment paper. It does not make an individual database model an experimental structure.
5. **Varadi M et al. (2022).** AlphaFold Protein Structure Database: massively expanding the structural coverage of protein-sequence space with high-accuracy models. *Nucleic Acids Research*, 50(D1), D439–D444. https://doi.org/10.1093/nar/gkab1061. Database confidence measures and storage of pLDDT in coordinate-file B-factor fields.
6. **Varadi M et al. (2024).** AlphaFold Protein Structure Database in 2024: providing structure coverage for over 214 million protein sequences. *Nucleic Acids Research*, 52(D1), D368–D375. https://doi.org/10.1093/nar/gkad1011. Database update; the number in the title describes that publication, not a current count asserted by this repository.
7. **Bertoni D et al. (2026).** AlphaFold Protein Structure Database 2025: a redesigned interface and updated structural coverage. *Nucleic Acids Research*, 54(D1), D358–D362. https://doi.org/10.1093/nar/gkaf1226. Current verified update. “2025” is part of the title; the journal issue is dated January 2026.
8. **EMBL-EBI AlphaFold training: pLDDT, understanding local confidence.** https://www.ebi.ac.uk/training/online/courses/alphafold/inputs-and-outputs/evaluating-alphafolds-predicted-structures-using-confidence-scores/plddt-understanding-local-confidence/. Used for interpretation boundaries, including the distinction between local confidence and relative domain positioning.

## Experimental structure interpretation

9. **RCSB PDB: assessing the quality of 3D structures.** https://www.rcsb.org/docs/general-help/assessing-the-quality-of-3d-structures. Geometry and experimental-data support address different aspects of an atomic model.
10. **wwPDB PDBx/mmCIF dictionary: `_atom_site.B_iso_or_equiv`.** https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_atom_site.B_iso_or_equiv.html. Definition and units of the experimental atomic displacement parameter.
11. **RCSB PDB-101: missing coordinates.** https://pdb101.rcsb.org/learn/guide-to-understanding-pdb-data/missing-coordinates. Why a deposited sequence can contain residues without corresponding coordinates.

Experimental entry choice, chain selection, sequence mapping, atom selection, and missing-coordinate handling are analysis decisions. Their recorded implementation is the evidence for the reported comparison; the general references above do not substitute for that record.

12. **Kabsch W. (1976).** A solution for the best rotation to relate two sets of vectors. *Acta Crystallographica A*, 32, 922–923. https://doi.org/10.1107/S0567739476001873. The least-squares rigid-fitting problem.

13. **Choudhary P et al. (2023).** Unified access to up-to-date residue-level annotations from UniProtKB and other biological databases for PDB data. *Scientific Data*, 10, 204. https://doi.org/10.1038/s41597-023-02101-6. SIFTS-based residue correspondence and numbering integration.
