# Biology and concepts behind the comparison

Terminology: [glossary](glossary.md). Scientific and operational choices: [assumptions](assumptions.md).

## Why use human carbonic anhydrase II?

Human carbonic anhydrase II, also called CAII (encoded by the human CA2 gene), is the enzyme represented by [UniProt P00918](https://www.uniprot.org/uniprotkb/P00918/entry). It catalyzes the reversible reaction:

**CO₂ + H₂O ⇌ HCO₃⁻ + H⁺**

This connects dissolved carbon dioxide with bicarbonate and protons. Carbonic anhydrases help carbon dioxide handling and acid–base balance; CAII's biological role is much broader than the coordinate file examined here ([UniProt P00918](https://www.uniprot.org/uniprotkb/P00918/entry)). The zinc-dependent catalytic background is reviewed by [McCall et al. (2000)](https://doi.org/10.1093/jn/130.5.1437S). The enzyme speeds the approach to equilibrium; it does not change the equilibrium itself.

CAII is a useful teaching example because its sequence, chemistry, and experimental structures are well studied. The project asks how different kinds of structural evidence can be compared. It does not test a new enzyme, propose sequence changes, or measure function.

## What the metal contributes

CAII is a metalloenzyme: the native catalytic site contains zinc. Three histidine side chains coordinate the metal, with a water-derived ligand participating in the catalytic chemistry. The surrounding protein and solvent environment matters as well ([UniProt P00918](https://www.uniprot.org/uniprotkb/P00918/entry); [Håkansson et al., 1992](https://doi.org/10.1016/0022-2836%2892%2990531-n)).

A drawing of the fold is therefore not the whole enzyme. Metal occupancy, water positions, protonation, and solution conditions can matter without producing a large change in the overall backbone. If a prediction omits zinc or water, that omission is a limitation of the represented model, not evidence that the biological protein lacks them. This comparison does not calculate catalytic rates or metal-binding affinity.

## Experimental coordinates and predictions answer different questions

An X-ray structure is an atomic model interpreted from diffraction data. The coordinates are supported to different degrees by the experiment, and their interpretation also depends on resolution, refinement, crystal conditions, and model validation. They are not a literal photograph of one freely moving molecule. [RCSB's validation guide](https://www.rcsb.org/docs/general-help/assessing-the-quality-of-3d-structures) explains why data-fit and geometry checks both matter.

An AlphaFold model is a computational prediction informed by learned structural patterns and its inputs. The original AlphaFold2 study established strong prediction performance in assessed settings, but did not establish that every model represents every functional state ([Jumper et al., 2021](https://doi.org/10.1038/s41586-021-03819-2)). A database prediction and a crystal structure are useful to compare precisely because their evidence and assumptions differ.

One protein comparison is a case study, not a general accuracy benchmark. Without auditing training and template provenance, agreement with a known structure should not be presented as a fully independent prediction test.

## Confidence is not an experimental measurement

AlphaFold's predicted local distance difference test (pLDDT) score estimates confidence in local structural accuracy on a 0–100 scale. Higher values indicate greater model confidence, not a guarantee of correctness or proof of biological activity. Local confidence also does not by itself establish the relative arrangement of distant regions; AlphaFold provides a separate predicted aligned error (PAE) measure for that question ([EMBL-EBI confidence guide](https://www.ebi.ac.uk/training/online/courses/alphafold/inputs-and-outputs/evaluating-alphafolds-predicted-structures-using-confidence-scores/plddt-understanding-local-confidence/)).

The same file column can mean different things:

| Value | What it describes |
| --- | --- |
| Experimental B factor | An atomic displacement parameter used in the crystallographic model, reported in square ångströms. |
| AlphaFold DB pLDDT | A dimensionless predicted local-confidence score, stored in the B-factor field of downloaded coordinate files. |

These values cannot be interpreted as equivalent measurements or compared on one shared quality scale ([wwPDB dictionary](https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_atom_site.B_iso_or_equiv.html); [Varadi et al., 2022](https://doi.org/10.1093/nar/gkab1061)). A low-confidence predicted region is also not sufficient evidence that the region is intrinsically disordered in every setting.

## What alignment and RMSD can show

Before superposing structures, the analysis must establish which residues correspond. UniProt sequence positions, deposited residue labels, insertion codes, and residues with observed coordinates are related concepts, but they are not interchangeable. Missing coordinates do not mean that the residue was absent from the biological sequence. A region may lack interpretable experimental density ([RCSB: missing coordinates](https://pdb101.rcsb.org/learn/guide-to-understanding-pdb-data/missing-coordinates)).

Root-mean-square deviation (RMSD) summarizes the distances between matched atoms after a specified fit. Its meaning depends on which atoms were included, the alignment, and the fitted subset. A backbone comparison based on matched alpha-carbon (Cα) atoms does not assess all side chains, metal geometry, waters, or alternative conformations. Excluding difficult regions can reduce RMSD while concealing the very differences a reader needs to see.

Report the atom selection and coverage alongside the number. Small RMSD supports geometric similarity over that selection; it does not demonstrate identical dynamics, stability, catalytic activity, or binding affinity. Different constructs and experimental states may also make a simple one-to-one comparison incomplete.

## The selected structures and numbering

[2CBA chain A](https://www.rcsb.org/structure/2CBA) is a zinc-bound, 1.54 Å X-ray model with no reported amino-acid mutations. Its chemical representation nevertheless differs: the deposited 260-position polymer begins with an acetyl (ACE) cap rather than UniProt Met1; neither ACE1 nor Ser2 has a Cα coordinate. [SIFTS](https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/2cba) maps entity positions 2–260 to UniProt 2–260, with 258 matched alpha-carbon (Cα) atoms available. Author numbering jumps from 125 to 127: author 127 corresponds to UniProt 126, so that jump is not a missing residue. [AF-P00918-F1 v6](../data/alphafold_P00918.json) was generated on 1 August 2025 using the AlphaFold Monomer v2.0 pipeline. Because 2CBA was available before AlphaFold2 training and the prediction’s exact training/template provenance has not been audited, overlap cannot be excluded; fitted RMSD is descriptive, not an independent generalization benchmark.

## What this project can reasonably conclude

The analysis can document sequence correspondence, represented residues, local prediction confidence, and coordinate similarity for one chosen comparison. It can make gaps in the evidence visible. It cannot establish a reaction mechanism from the model alone, validate activity, rank inhibitors, or support clinical claims.

The most useful result is an explicit account of what was compared and what remains uncertain. Source records and file versions should travel with that account. The [references](references.md) separate biochemical background, prediction methods, database documentation, and experimental-model interpretation.
