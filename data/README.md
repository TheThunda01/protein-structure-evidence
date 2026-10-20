# Source snapshots and reuse

These are public scientific records downloaded on 20 October 2026. `provenance.json` records each source URL, byte count, SHA-256, and serialization convention. Analysis verifies all eight files before calculating results.

| Source | Files and attribution | Reuse conditions |
| --- | --- | --- |
| wwPDB/RCSB, 2CBA | `2cba.pdb`; entry, entity, and chain metadata. Cite Håkansson et al. (1992), DOI [10.1016/0022-2836(92)90531-N](https://doi.org/10.1016/0022-2836(92)90531-N), and [the PDB entry](https://doi.org/10.2210/pdb2cba/pdb). | PDB archive coordinates use [CC0 1.0](https://www.wwpdb.org/about/usage-policies). RCSB metadata contains attributed third-party annotations; retain source attribution and applicable provider terms. |
| UniProt Consortium, P00918 | `uniprot_P00918.json`; entry version 279, sequence version 2; [official entry](https://www.uniprot.org/uniprotkb/P00918/entry). | [CC BY 4.0](https://www.uniprot.org/help/license). |
| Google DeepMind / EMBL-EBI AlphaFold DB | `alphafold_P00918.json`, model-v6 PDB, and confidence JSON. Cite [Jumper et al. (2021)](https://doi.org/10.1038/s41586-021-03819-2) and the [database update](https://doi.org/10.1093/nar/gkaf1226). | [CC BY 4.0](https://alphafold.ebi.ac.uk/faq). |

The project's MIT license covers its code, not a replacement license for these data. The structural comparison and figures are derived from the attributed records above; retain that attribution when reusing the results.

Coordinate files are unmodified. API JSON snapshots are reformatted only, preserving their values. The optional retrieval script reproduces that formatting and requires the same hashes. Updated online metadata or coordinates can cause retrieval to stop; review changes explicitly rather than silently replacing a pinned case.

No new structure prediction, experimental measurement, protein design, or sequence generation was performed. The canonical sequence and structure coordinates are existing public records for the human CAII case study.
