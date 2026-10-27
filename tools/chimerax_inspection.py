"""Run inside ChimeraX to inspect the verified, already aligned model pair.

Example: ChimeraX --exit --script "tools/chimerax_inspection.py --output-dir derived/chimerax-001"
Use --no-render for a command-line-only model/attribute check.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def inspect(session, output, render=True):
    from chimerax.core.commands import run
    from chimerax.atomic import AtomicStructure
    import chimerax.core
    from verify_alignment import verify_bundle

    output = Path(output).absolute()
    if output.exists() or any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError("Choose a new output directory without symlinks")
    if any(output.resolve().is_relative_to(ROOT / name) for name in ("data", "results", "examples")):
        raise ValueError("Write inspection outputs outside the recorded data/results/examples")
    if session.models.list():
        raise ValueError("Open this script in a new ChimeraX session; existing models are preserved")
    # Numerical verification precedes opening: the viewer never chooses a fit.
    checked = verify_bundle(ROOT / "data", ROOT / "examples/alignment")
    source = ROOT / "data/2cba.pdb"
    aligned = ROOT / "examples/alignment/aligned_prediction.pdb"
    for path, identifier in ((source, 1), (aligned, 2)):
        run(session, f'open "{path.as_posix()}" id #{identifier}')
    models = session.models.list(type=AtomicStructure)
    if len(models) != 2:
        raise ValueError("Expected the two atomic models")
    summary = {"schema_version": 1, "chimerax_version": chimerax.core.__version__,
        "fit": "Uses the verified saved transform; no fit or coordinate change in ChimeraX",
        "verification": checked,
        "models": [{"id": model.id_string, "atoms": model.num_atoms,
                    "residues": model.num_residues} for model in models],
        "source_sha256": {"data/2cba.pdb": hashlib.sha256(source.read_bytes()).hexdigest(),
                          "examples/alignment/aligned_prediction.pdb": hashlib.sha256(aligned.read_bytes()).hexdigest()},
        "scope": "Visualization of one pinned pair; training/template overlap cannot be excluded. Confidence and experimental B factors remain distinct.",
        "rendered": render}
    if render and not session.ui.is_gui:
        raise ValueError("Rendering needs a graphical ChimeraX session; use --no-render with --nogui")
    output.mkdir(parents=True)
    if render:
        commands = ["set bgColor white", "camera ortho", "lighting soft", "graphics silhouettes true",
            "hide atoms", "cartoon #1/A", "cartoon #2/A", "color #1 #176b87", "color #2 #d58027",
            "show #1:ZN atoms", "style #1:ZN sphere", "color #1:ZN #7a477e", "view orient",
            "view #1,2", "turn y 25", "turn x -10", "zoom 0.72",
            '2dlabels create title text "Carbonic anhydrase II: verified coordinate overlay" xpos 0.03 ypos 0.93 size 24 color black',
            '2dlabels create experiment text "Teal: experimental 2CBA chain A" xpos 0.03 ypos 0.08 size 19 color #176b87',
            '2dlabels create prediction text "Orange: aligned AlphaFold P00918 v6" xpos 0.03 ypos 0.035 size 19 color #b36819',
            f'save "{(output / "overlay.png").as_posix()}" width 1400 height 1050 supersample 3',
            f'save "{(output / "inspection.cxs").as_posix()}"']
        for command in commands:
            run(session, command)
        summary["commands"] = [c.replace(output.as_posix(), "<output>") for c in commands]
        summary["image_sha256"] = hashlib.sha256((output / "overlay.png").read_bytes()).hexdigest()
    (output / "inspection.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "models": summary["models"], "rendered": render}))


if __name__ == "__main__" or "session" in globals():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args()
    if "session" not in globals():
        parser.error("Run this script inside ChimeraX, as shown in the usage example")
    inspect(session, args.output_dir, not args.no_render)
