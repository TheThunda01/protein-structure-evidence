# Reproduce the molecular-viewer inspection

The ChimeraX workflow opens the experimental model and the already transformed prediction in one coordinate frame. It calls the existing alignment-bundle verifier first, then draws the structures without applying another fit. This connects the inspected model to the project's explicit residue mapping and fit selection.

## Run in a new session

Install [UCSF ChimeraX](https://www.rbvi.ucsf.edu/chimerax/download.html) under its applicable license. It is optional and separate from the core Python requirements. From the repository root, run the command below, replacing `ChimeraX` with the executable's path if needed:

```sh
ChimeraX --exit --script "tools/chimerax_inspection.py --output-dir derived/chimerax-001"
```

The output directory must be new and outside `data/`, `results/`, and `examples/`. Existing destinations and symlink paths are refused. The script refuses a session that already has models rather than clearing the user's scene. Running in a fresh application process also prevents previously changed camera and display settings from influencing the view.

For import and numerical verification without rendering:

```sh
ChimeraX --nogui --exit --script "tools/chimerax_inspection.py --output-dir derived/chimerax-check-001 --no-render"
```

The rendered workflow creates:

| File | Purpose |
| --- | --- |
| `overlay.png` | Labeled cartoon view with an orthographic camera. Teal is experimental 2CBA chain A; orange is the aligned AlphaFold v6 model. Experimental zinc is shown in purple. |
| `inspection.cxs` | Native ChimeraX session for rotation, selections, and inspection. Preserve it separately from a new edited session. |
| `inspection.json` | Input hashes, alignment verification, application version, displayed model counts, render commands, and image fingerprint. |

`--no-render` writes only `inspection.json`. A failure before model import or rendering does not establish success; require the completed JSON report and expected outputs. Rendering depends on the local graphical stack. Camera and styling commands are recorded, but pixel-identical output across GPUs and software versions is not promised.

## What was checked

On 27 October 2026, ChimeraX 1.12 opened both pinned models and saved a 1,400 × 1,050 PNG and native session. The verifier recomputed the existing 258-pair fit and checked the saved coordinates. ChimeraX's bundled Python/NumPy versions differ from the original analysis runtime; the report retains that mismatch while the existing numerical tolerances passed. The core analysis and tests were also run in the repository's pinned dependency versions separately.

ChimeraX reported 2,280 atoms in the experimental model and 2,073 in the prediction. These are viewer model counts, including nonprotein residues in the experimental model, rather than fit denominators. The displayed cartoon uses the viewer's representation choices; the fit still uses the 258 mapped Cα pairs in the verified bundle.

The committed [preview](figures/chimerax-overlay.png) and [render record](figures/chimerax-overlay.json) come from this run. The generated native session stays in `derived/`, which is ignored by Git; the small Python script is the portable editable source.

## Interpretation

The view shows geometric agreement in one pinned structure pair. It is not an independent prediction benchmark: training/template overlap cannot be excluded. It does not assess active-site chemistry, side-chain accuracy, binding, dynamics, or activity. No predicted zinc or other atoms were added.

The original experimental B factors and predicted pLDDT values remain unchanged in their respective models. The overlay colors identify the source model; they do not combine those quantities into one confidence scale. See [methods](methods.md), [source terms](../data/README.md), and the official ChimeraX [save](https://www.rbvi.ucsf.edu/chimerax/docs/user/commands/save.html) and [view](https://www.rbvi.ucsf.edu/chimerax/docs/user/commands/view.html) documentation for the distinct scientific and display choices.
