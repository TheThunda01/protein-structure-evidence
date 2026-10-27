# Project context

Terminology: [glossary](glossary.md). Scientific and operational choices: [assumptions](assumptions.md).

## Background and rationale

A protein structure describes an atomic model; it does not directly reveal everything a protein does. Experimental models, predicted coordinates, sequence annotations, and confidence scores answer related but different questions. This project compares those sources for human carbonic anhydrase II, a zinc-containing enzyme, and shows which assumptions lie behind a structural similarity score.

The project asks: **which residues can be compared, how similar are their backbone positions after a rigid fit, and what does the available evidence leave unresolved?** The [biology guide](biology-and-concepts.md) explains the enzyme and the structural concepts.

## What it does

The analysis compares a pinned [AlphaFold DB prediction](https://alphafold.ebi.ac.uk/entry/P00918) with [experimental structure 2CBA](https://www.rcsb.org/structure/2CBA). It maps author residue numbers through the deposited sequence to UniProt positions, checks amino-acid identities, and compares overlapping Cα coordinates. Separate outputs show missing positions, predicted pLDDT, experimental B factors, fitting sensitivity, and a few experimental zinc-neighbor distances.

## Why it matters

This case shows why mapping must precede alignment. Author numbering skips a number even though the canonical sequence does not. The models also differ in their N-terminal chemical state, and some positions lack comparable experimental coordinates. An overlay alone can conceal these differences.

The project traces source records, joins biological databases, tests the geometry calculations, and states what the comparison can support. A low RMSD measures geometric agreement over selected atoms; it does not establish activity or affinity.

## Main themes

- **Correspondence:** compare the same residues before comparing coordinates.
- **Evidence types:** keep predictions, measurements, and annotations distinct.
- **Reproducibility:** preserve source versions, mappings, and fit selections.
- **Limits:** report what is not represented or independently tested.

The historical experimental structure may overlap AlphaFold training data or templates. This is a worked comparison, not an independent benchmark of prediction accuracy or a validation of biological function.

## Where this fits in the portfolio

This is a supporting study of what a model comparison can establish. It complements the featured [enzyme kinetics study](https://github.com/TheThunda01/enzyme-kinetics-workbench), which distinguishes a fitted curve from evidence about its parameters and mechanism. The studies use different proteins and inputs. The [portfolio guide](https://github.com/TheThunda01/TheThunda01/blob/main/PROJECT_GUIDE.md) places both alongside prediction checks and virtual measurement selection.
