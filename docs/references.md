# References and how they are used

Checked on **20 October 2026**. The [reference audit](reference-audit.json) records access and metadata status for every source below. An abstract check is not a full-text appraisal. These sources support background or method choices; none independently validates this repository’s results. See the [glossary](glossary.md) and [assumptions](assumptions.md) for interpretation.

## Research and methods

- McCall, K. A., Huang, C., & Fierke, C. A. (2000). Function and mechanism of zinc metalloenzymes. *The Journal of Nutrition, 130*(5S Suppl), 1437S–1446S. [doi:10.1093/jn/130.5.1437S](https://doi.org/10.1093/jn/130.5.1437S). [PMID: 10801957](https://pubmed.ncbi.nlm.nih.gov/10801957/). Conceptual background on zinc metalloenzymes and coordination-dependent catalytic chemistry. Review, not a primary experiment or evidence of activity measured here.

- Håkansson, K., Carlsson, M., Svensson, L. A., & Liljas, A. (1992). Structure of native and apo carbonic anhydrase II and structure of some of its anion-ligand complexes. *Journal of Molecular Biology, 227*(4), 1192–1204. [doi:10.1016/0022-2836(92)90531-n](https://doi.org/10.1016/0022-2836%2892%2990531-n). [PMID: 1433293](https://pubmed.ncbi.nlm.nih.gov/1433293/). Primary carbonic anhydrase II structures and zinc-site context. Several structures/states are covered; entry-specific facts use 2CBA metadata.

- Jumper, J., et al. (2021). Highly accurate protein structure prediction with AlphaFold. *Nature, 596*(7873), 583–589. [doi:10.1038/s41586-021-03819-2](https://doi.org/10.1038/s41586-021-03819-2). [PMID: 34265844](https://pubmed.ncbi.nlm.nih.gov/34265844/). AlphaFold2 method and assessed prediction performance. Does not establish case-specific independent generalization or biochemical function.

- Varadi, M., et al. (2022). AlphaFold Protein Structure Database: massively expanding the structural coverage of protein-sequence space with high-accuracy models. *Nucleic Acids Research, 50*(D1), D439–D444. [doi:10.1093/nar/gkab1061](https://doi.org/10.1093/nar/gkab1061). [PMID: 34791371](https://pubmed.ncbi.nlm.nih.gov/34791371/). Original AlphaFold Database organization and model-confidence context. Historical database coverage is not a current count.

- Varadi, M., et al. (2024). AlphaFold Protein Structure Database in 2024: providing structure coverage for over 214 million protein sequences. *Nucleic Acids Research, 52*(D1), D368–D375. [doi:10.1093/nar/gkad1011](https://doi.org/10.1093/nar/gkad1011). [PMID: 37933859](https://pubmed.ncbi.nlm.nih.gov/37933859/). 2024 AlphaFold Database update. Coverage in title refers to that publication.

- Bertoni, D., et al. (2026). AlphaFold Protein Structure Database 2025: a redesigned interface and updated structural coverage. *Nucleic Acids Research, 54*(D1), D358–D362. [doi:10.1093/nar/gkaf1226](https://doi.org/10.1093/nar/gkaf1226). [PMID: 41273079](https://pubmed.ncbi.nlm.nih.gov/41273079/). Database update aligned to UniProt 2025_03; interface and provenance context. The title says 2025 but the journal issue year is 2026.

- Choudhary, P., et al. (2023). Unified access to up-to-date residue-level annotations from UniProtKB and other biological databases for PDB data. *Scientific Data, 10*(1), 204. [doi:10.1038/s41597-023-02101-6](https://doi.org/10.1038/s41597-023-02101-6). [PMID: 37045837](https://pubmed.ncbi.nlm.nih.gov/37045837/). SIFTS residue correspondence and integration of structure/sequence annotations. A mapping is not proof of identical chemical states.

- Zhang, C., Shine, M., Pyle, A. M., & Zhang, Y. (2022). US-align: universal structure alignments of proteins, nucleic acids, and macromolecular complexes. *Nature Methods, 19*(9), 1109–1115. [doi:10.1038/s41592-022-01585-1](https://doi.org/10.1038/s41592-022-01585-1). [PMID: 36038728](https://pubmed.ncbi.nlm.nih.gov/36038728/). US-align is a structural-alignment search method using a TM-score objective. It differs from this fixed-correspondence least-squares fit; no performance is transferred.

- Zhang, C., Freddolino, L., & Zhang, Y. (2026). A graphic and command line protocol for quick and accurate comparisons of protein and nucleic acid structures with US-align. *Nature Protocols, 21*(2), 517–541. [doi:10.1038/s41596-025-01189-x](https://doi.org/10.1038/s41596-025-01189-x). [PMID: 40604267](https://pubmed.ncbi.nlm.nih.gov/40604267/). US-align comparison/export protocol context. Protocol is supplementary practice context; the tool was not benchmarked here.

- Tauriello, G., et al. (2026). ModelCIF Update: Supporting Emerging Classes of Computational Macromolecular Models. *Journal of Molecular Biology, 438*(18), 169658. [doi:10.1016/j.jmb.2026.169658](https://doi.org/10.1016/j.jmb.2026.169658). [PMID: 41580068](https://pubmed.ncbi.nlm.nih.gov/41580068/). ModelCIF represents computational models with explicit protocols, inputs and outputs. The project is not ModelCIF-compliant.

- Kabsch, W. (1976). A solution for the best rotation to relate two sets of vectors. *Acta Crystallographica Section A, 32*(5), 922–923. [doi:10.1107/S0567739476001873](https://doi.org/10.1107/S0567739476001873). Least-squares rigid rotation formulation. Publisher abstract/metadata inspected; no claim of complete article review.

## Data, software, standards, and reuse

- UniProt Consortium. (n.d.). *UniProtKB P00918 (CAH2_HUMAN)* [Dataset], entry 279; sequence 2. [Source](https://www.uniprot.org/uniprotkb/P00918/entry). Human carbonic anhydrase II identity, 260-residue sequence, catalytic annotation and metal-binding features. Pinned REST record and live REST metadata inspected; web entry renders only a fallback shell. Annotations summarize external evidence.

- K. Håkansson / M. Carlsson / L. A. Svensson / A. Liljas. (1993). *PDB 2CBA: carbonic anhydrase II* [Dataset], pinned files in data/provenance.json. [doi:10.2210/pdb2cba/pdb](https://www.rcsb.org/structure/2CBA). 1.54 Å X-ray entry, no reported mutations, deposited chemistry, residue identifiers and ligand context.

- Google DeepMind / EMBL-EBI. (2025). *AlphaFold Database P00918 model and confidence* [Dataset], AF-P00918-F1-model_v6; generated 2025-08-01. [Source](https://alphafold.ebi.ac.uk/entry/P00918). Pinned model coordinates, confidence values, model creation date and pipeline annotation. Pinned local official snapshots inspected. These data are predictions, not new experimental coordinates.

- EMBL-EBI. (n.d.). *pLDDT: Understanding local confidence* [Official documentation]. [Source](https://www.ebi.ac.uk/training/online/courses/alphafold/inputs-and-outputs/evaluating-alphafolds-predicted-structures-using-confidence-scores/plddt-understanding-local-confidence/). pLDDT is a local-confidence score; high local confidence does not establish domain orientation or function.

- RCSB PDB. (n.d.). *Assessing the quality of 3D structures* [Official documentation]. [Source](https://www.rcsb.org/docs/general-help/assessing-the-quality-of-3d-structures). Experimental data fit and geometry are distinct quality considerations.

- wwPDB. (n.d.). *PDBx/mmCIF dictionary: _atom_site.B_iso_or_equiv* [Official documentation], PDBx/mmCIF V5. [Source](https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_atom_site.B_iso_or_equiv.html). Definition of isotropic atomic displacement parameters and units.

- RCSB PDB-101. (n.d.). *Missing coordinates* [Official documentation]. [Source](https://pdb101.rcsb.org/learn/guide-to-understanding-pdb-data/missing-coordinates). Sequence presence and modeled coordinates are different.

- RCSB PDB. (n.d.). *Identifiers in PDB* [Official documentation]. [Source](https://www.rcsb.org/docs/general-help/identifiers-in-pdb). Author, entity and sequence identifiers need explicit mapping.

- wwPDB. (n.d.). *Atomic Coordinate Entry Format: coordinate section* [Official documentation], 3.3. [Source](https://www.wwpdb.org/documentation/file-format-content/format33/sect9.html). Fixed-width atom coordinates, occupancy, temperature-factor and alternate-location fields.

- wwPDB. (n.d.). *Atomic Coordinate Entry Format: crystallographic and coordinate transformation section* [Official documentation], 3.3. [Source](https://www.wwpdb.org/documentation/file-format-content/format33/sect8.html). Coordinate-frame transformation fields must not be retained with invalid meaning after export.

- Chengxin Zhang / Lydia Freddolino / Anna Marie Pyle / Yang Zhang. (n.d.). *US-align source and readme* [Software], 20261019; commit 23f14ffcf8647f2dc1c0e01043db3a7f3a661c28. [Source](https://github.com/pylelab/USalign/tree/23f14ffcf8647f2dc1c0e01043db3a7f3a661c28). Comparison/export practice and custom permissive license context. Readme inspected through GitHub connector after web fetch failed; source was not copied and no benchmark was run.

- Python Software Foundation. (n.d.). *Python hashlib library documentation* [Official documentation], 3.12.15. [Source](https://docs.python.org/3.12/library/hashlib.html). Byte digests identify file content.

- Python Software Foundation. (n.d.). *Python hmac library documentation* [Official documentation], 3.12.15. [Source](https://docs.python.org/3.12/library/hmac.html). Keyed authentication differs from unsigned hashes.

- Python Software Foundation. (n.d.). *Python json library documentation* [Official documentation], 3.12.15. [Source](https://docs.python.org/3.12/library/json.html). Decoder hooks and size restrictions support explicit parsing.

- wwPDB. (n.d.). *PDB usage policies* [Official documentation]. [Source](https://www.wwpdb.org/about/usage-policies). PDB archive data use CC0 with encouraged attribution.

- UniProt Consortium. (n.d.). *UniProt license* [Official documentation]. [Source](https://www.uniprot.org/help/license). Existing source provenance records CC BY 4.0 for the bundled UniProt data. Live page returned a JavaScript fallback shell; license text could not be independently reread here. Existing license/provenance was preserved, not replaced.

- EMBL-EBI. (n.d.). *AlphaFold Database frequently asked questions* [Official documentation]. [Source](https://alphafold.ebi.ac.uk/faq). Existing source provenance records the database reuse terms. Only rendered page shell was accessible in this recheck; the FAQ answers and reuse text were not exposed. Existing attribution and CC BY 4.0 notice remain unchanged.
