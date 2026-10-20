"""Reproduce the pinned carbonic-anhydrase structure comparison offline."""

import argparse
import csv
import json
import os
from pathlib import Path
import tempfile

import numpy as np

from structure_evidence import ValidationError, comparison, sha256


def rounded(value):
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, dict):
        return {k: rounded(v) for k, v in value.items()}
    if isinstance(value, list):
        return [rounded(v) for v in value]
    return value


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rounded(rows))


def figures(result, directory):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    rows = result["residues"]
    positions = [r["uniprot_position"] for r in rows]
    values = lambda key: [np.nan if r[key] is None else r[key] for r in rows]
    fig, axes = plt.subplots(3, 1, figsize=(11, 8.4), sharex=True, layout="constrained")
    axes[0].plot(positions, values("predicted_plddt"), color="#007c91", lw=1.5)
    axes[0].set(ylabel="Predicted pLDDT\n(dimensionless)", ylim=(0, 103))
    axes[0].axhline(70, color="#aaaaaa", linestyle="--", lw=.7)
    axes[0].axhline(90, color="#aaaaaa", linestyle="--", lw=.7)
    axes[1].plot(positions, values("ca_displacement_A"), color="#c26020", lw=1.2)
    axes[1].set(ylabel="Cα displacement (Å)\nafter rigid fitting", ylim=(0, None))
    axes[2].plot(positions, values("experimental_ca_b_factor_A2"), color="#7151a0", lw=1.2)
    axes[2].set(ylabel="Experimental Cα B\n(Å²)", xlabel="UniProt P00918 residue position", ylim=(0, None))
    for ax in axes:
        ax.axvspan(.5, 2.5, color="#cccccc", alpha=.5)
        ax.grid(alpha=.15)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Human CAII: three different evidence summaries\nShaded positions 1–2 lack comparable experimental Cα coordinates", fontsize=13)
    fig.savefig(directory / "evidence_profiles.png", dpi=160, metadata={"Software": "protein-structure-evidence"})
    plt.close(fig)
    fig = plt.figure(figsize=(8.5, 7), layout="constrained")
    ax = fig.add_subplot(111, projection="3d")
    exp, pred = result["experimental_xyz"], result["aligned_predicted_xyz"]
    ax.plot(*exp.T, color="#425879", lw=1.4, alpha=.85, label="Experimental 2CBA chain A")
    ax.plot(*pred.T, color="#d07b2c", lw=1.2, alpha=.75, label="AlphaFold DB v6, fitted")
    zinc = np.asarray(result["experimental_zinc_xyz"])
    ax.scatter(*zinc, color="#d6aa00", edgecolor="black", s=60, label="Experimental zinc only")
    combined = np.vstack([exp, pred])
    ax.set_box_aspect(np.ptp(combined, axis=0))
    ax.set(xlabel="x (Å)", ylabel="y (Å)", zlabel="z (Å)", title="Matched Cα traces after a proper rigid fit\nNo predicted metal ion was added")
    ax.legend(loc="upper left", fontsize=9)
    ax.view_init(elev=20, azim=-63)
    fig.savefig(directory / "backbone_overlay.png", dpi=160, metadata={"Software": "protein-structure-evidence"})
    plt.close(fig)


def run(data_dir, output_dir, fit_min_plddt=0.0, make_figures=True):
    if data_dir.resolve() == output_dir.resolve():
        raise ValidationError("Keep output separate from source data")
    result = comparison(data_dir, fit_min_plddt)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".structure_results_", dir=output_dir.parent) as temp:
        directory = Path(temp)
        summary = rounded(result["summary"])
        summary["source_manifest_sha256"] = sha256(data_dir / "provenance.json")
        summary["plots_generated"] = make_figures
        (directory / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
        write_csv(directory / "residue_comparison.csv", result["residues"])
        write_csv(directory / "fit_sensitivity.csv", result["fit_sensitivity"])
        write_csv(directory / "zinc_geometry.csv", result["zinc_geometry"])
        lines = ["# Carbonic anhydrase II: descriptive structure comparison", "",
                 f"Compared {summary['matched_ca_residues']} mapped Cα pairs. The selected fit used {summary['fit_residues']} positions and a pLDDT inclusion threshold of {fit_min_plddt:g}.", "",
                 f"- Fitted-set Cα RMSD: **{summary['fit_rmsd_A']:.3f} Å**.",
                 f"- RMSD evaluated across all mapped pairs: **{summary['all_matched_ca_rmsd_A']:.3f} Å**.",
                 f"- Largest fitted displacement: **{summary['max_ca_displacement_A']:.3f} Å**, at UniProt residue **{summary['max_displacement_uniprot_position']}**.",
                 "- No comparable experimental Cα is available for canonical positions **1–2**. Position 1 also differs chemically: the PDB declares an ACE group rather than canonical methionine.", "",
                 "Author numbering is not canonical numbering: author residue 127 maps to UniProt 126. The missing author number 126 is not evidence of a missing amino acid.", "",
                 "pLDDT and experimental B factors are kept separate. The former is predicted local confidence; the latter is an experimental model displacement parameter. Neither is an activity or affinity measurement.", "",
                 "The structure is a familiar historical protein, and 2CBA predates AlphaFold training. Training or template overlap cannot be excluded. This is not an independent prediction benchmark; small fitted RMSD does not validate generalization. Differences can reflect chemical state, environment, incomplete experimental modeling, prediction, and fitting choices; this analysis cannot separate their causes.", ""]
        (directory / "report.md").write_text("\n".join(lines), encoding="utf-8")
        if make_figures:
            figures(result, directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        for source in directory.iterdir():
            os.replace(source, output_dir / source.name)
        if not make_figures:
            for name in ("evidence_profiles.png", "backbone_overlay.png"):
                (output_dir / name).unlink(missing_ok=True)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--fit-min-plddt", type=float, default=0)
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    try:
        summary = run(args.data_dir, args.output_dir, args.fit_min_plddt, not args.no_plots)
    except (ValidationError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.exit(2, f"Analysis stopped: {error}\n")
    print(f"Compared {summary['matched_ca_residues']} Cα pairs; RMSD {summary['all_matched_ca_rmsd_A']:.6f} Å")
