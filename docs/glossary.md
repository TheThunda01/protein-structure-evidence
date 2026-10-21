# Glossary

These definitions explain the terms used in this project. Read them alongside the [methods](methods.md) and [assumptions](assumptions.md); a familiar label does not establish a result’s validity.

| Term | Meaning here |
| --- | --- |
| Protein; amino acid; residue | A protein is a chain of amino acids; a residue is one amino-acid unit within that chain. |
| CAII; CA2 | Carbonic anhydrase II is the protein studied here. CA2 is the human gene symbol; P00918 is its UniProt accession. |
| Enzyme; catalysis; equilibrium | An enzyme speeds a chemical reaction. Catalysis changes how quickly equilibrium is approached, not the equilibrium constant. |
| Bicarbonate; proton; acid–base balance | Bicarbonate is HCO₃⁻; a proton is H⁺ in the reaction notation. Their balance contributes to control of acidity. |
| Metalloenzyme; cofactor; ligand | A metalloenzyme requires a metal for its usual activity. A cofactor is a nonprotein component involved in function; a ligand binds an atom or molecule, including zinc here. |
| Histidine; donor atom; protonation | Histidine is an amino acid whose side chain can coordinate zinc. A donor atom supplies electron density to a coordination interaction. Protonation describes where hydrogen ions are associated. |
| Canonical sequence; accession; sequence version | A database reference sequence, its stable identifier, and the revision number of that sequence. Annotation versions can change without changing sequence. |
| PDB; RCSB; wwPDB | Protein Data Bank; its US data center, the Research Collaboratory for Structural Bioinformatics; and the worldwide partnership maintaining the archive. |
| Chain; polymer entity; author numbering | A chain is an instance in a structure. A polymer entity identifies its molecular sequence. Author numbering is the depositor’s residue labeling and need not equal sequence position. |
| SIFTS | Structure Integration with Function, Taxonomy and Sequences: database mapping between structure residues and biological sequence annotations. |
| Cα; backbone; side chain | Cα is the alpha-carbon atom of an amino acid. Backbone atoms form the repeating chain; side chains distinguish amino acids. A Cα trace omits most chemistry. |
| Met; Ser; His; ACE | Residue abbreviations for methionine, serine and histidine. ACE is an acetyl capping group, not methionine. |
| Å; Å²; resolution | An ångström is 10⁻¹⁰ meters; Å² is its square. Crystallographic resolution describes the scale of diffraction detail and is not a direct per-atom error bound. |
| X-ray diffraction; refinement | Diffraction measurements constrain an atomic model. Refinement adjusts model parameters against those measurements; deposited coordinates remain interpreted models. |
| Occupancy; alternate location | Occupancy is a modeled fraction for an atomic position. Alternate locations represent alternative modeled positions; selecting one does not establish a unique solution conformation. |
| B factor; atomic displacement parameter | An experimental model parameter describing the spread of modeled atomic scattering, including effects of motion, disorder and modeling limitations. It is not a direct measured trajectory or pLDDT score. |
| AlphaFold; AFDB; monomer | AlphaFold is a structure-prediction method. AFDB is the AlphaFold Protein Structure Database. A monomer model represents one protein chain, not its complete molecular environment. |
| pLDDT | Predicted local distance difference test: AlphaFold’s dimensionless local-confidence score, from 0 to 100. It is not a probability of activity or of whole-model correctness. |
| PAE | Predicted aligned error: a separate estimate relevant to uncertainty in relative positions of regions. This project does not analyze PAE. |
| Rigid fit; superposition; RMSD | A rigid fit rotates and translates a model without deformation. Superposition overlays models. Root-mean-square deviation is the square root of mean squared distances between specified corresponding atoms. |
| SVD; determinant; proper rotation | Singular value decomposition is the matrix factorization used to compute the fit. A rotation with determinant +1 preserves handedness; a reflection does not. |
| Euclidean distance; fit set; evaluation set | Straight-line spatial distance; the atoms used to choose the transform; and the atoms used to report a comparison. Different selections can yield different scores. |
| Generalization; training overlap | Generalization means performance on new examples. Training overlap means evaluation evidence may have been available during learning or template selection. |
| ModelCIF; mmCIF | ModelCIF records computational structural models and provenance; macromolecular Crystallographic Information File is a structured archive format. Neither is implemented by this legacy-PDB exporter. |
| Provenance; hash; SHA-256; receipt | Provenance records origins and processing. A hash is a content fingerprint; SHA-256 is the algorithm used here. A receipt lists derived files and their inputs; it is not an authenticated signature. |
| JSON; API; CLI; CI | JavaScript Object Notation is a structured text format. An application programming interface serves data or functions. A command-line interface runs commands; continuous integration runs automated repository checks. |
| HMAC; byte; MiB; floating point | A keyed message authentication code differs from an unkeyed hash. A byte stores eight bits; MiB is 1,048,576 bytes. Floating-point numbers approximate real numbers with finite precision. |
| MIT; CC0; CC BY | MIT is the code license. CC0 is a public-domain dedication; Creative Commons Attribution requires attribution. Each upstream source retains its applicable terms. |
