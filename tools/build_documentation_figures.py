"""Draw documentation figures from the committed structural comparison tables.

This does not refit structures or replace analysis outputs. Run from any directory.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
INK, TEAL, BLUE, AMBER, MUTED, PALE = "#203449", "#007F7B", "#386CB0", "#B87824", "#596773", "#EEF3F6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "svg.fonttype": "none", "svg.hashsalt": "protein-documentation-v1"})


def read_rows(relative):
    with (ROOT / relative).open(newline="") as handle:
        return list(csv.DictReader(handle))


def save(fig, out, name, title, description, previews):
    path = out / name
    fig.savefig(path, format="svg", bbox_inches="tight", facecolor="white",
                metadata={"Date": None, "Title": title, "Description": description})
    content = path.read_text()
    content = re.sub(r"(<svg\b[^>]*)(>)", r'\1 role="img" aria-labelledby="figure-title figure-desc"\2', content, count=1)
    content = re.sub(r"(<svg\b[^>]*>)", lambda m: m.group(1) + "\n<title id=\"figure-title\">" + html.escape(title) + "</title>\n<desc id=\"figure-desc\">" + html.escape(description) + "</desc>", content, count=1)
    path.write_text(content)
    if previews:
        previews.mkdir(parents=True, exist_ok=True)
        fig.savefig(previews / (Path(name).stem + ".png"), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def mapping_figure(out, previews):
    rows = {int(row["uniprot_position"]): row for row in read_rows("results/residue_comparison.csv")}
    positions = [1, 2, 3, 4, 124, 125, 126, 127]
    assert len(rows) == 260 and sum(row["included_in_fit"] == "True" for row in rows.values()) == 258
    fig, ax = plt.subplots(figsize=(9.7, 4.5))
    ax.set(xlim=(-2.35, 8.15), ylim=(-1.1, 3.1)); ax.axis("off")
    ax.text(-2.20, 2.85, "Match sequence positions before comparing coordinates", fontsize=16, weight="bold")
    ax.text(-2.20, 2.42, "Selected positions from the pinned CAII comparison • the ellipsis omits intervening positions", color=MUTED, fontsize=10.5)
    ax.text(-2.20, 1.70, "UniProt\nposition", va="center", weight="bold")
    ax.text(-2.20, 0.45, "2CBA author\nresidue label", va="center", weight="bold")
    for index, position in enumerate(positions):
        x = index + (0.5 if index >= 4 else 0)
        row = rows[position]; matched = row["experimental_ca_present"] == "True"
        for y, label in [(1.70, str(position)), (0.45, row["author_residue"] or "unmapped")]:
            fill = PALE if y == 1.70 else ("#E3F2EF" if matched else "#FAF0DE")
            edge = TEAL if matched else AMBER
            box = FancyBboxPatch((x-.40,y-.28), .8,.56, boxstyle="round,pad=.03,rounding_size=.08", facecolor=fill, edgecolor=edge, linewidth=1.4)
            ax.add_patch(box); ax.text(x,y,label,ha="center",va="center",fontsize=9 if label=="unmapped" else 10.5)
        if row["author_residue"]:
            ax.annotate("",xy=(x,.78),xytext=(x,1.38),arrowprops={"arrowstyle":"->","color":TEAL if matched else AMBER,"linestyle":"-" if matched else "--","lw":1.4})
        ax.text(x,-.15,"Cα pair" if matched else "no Cα pair",ha="center",color=TEAL if matched else AMBER,fontsize=9)
    ax.text(3.75,1.72,"…",ha="center",fontsize=22,color=MUTED)
    ax.text(-2.20,-.70,"Positions 1–2 contribute no experimental Cα pair. Author 127 maps to UniProt 126; a label gap is not a missing residue.",fontsize=10.4)
    title = "CAII residue numbering and coordinate availability"
    description = "Eight selected canonical positions show their experimental author labels. Positions 1 and 2 have no matched experimental alpha carbon. Canonical positions 126 and 127 map to author labels 127 and 128. The plot is a positional schematic, not an atomic structure."
    save(fig,out,"residue-mapping.svg",title,description,previews)


def selection_figure(out, previews):
    rows = read_rows("results/fit_sensitivity.csv")
    assert [int(row["fit_residues"]) for row in rows] == [258,257,256]
    x = list(range(len(rows)))
    fit = [float(row["fit_rmsd_A"]) for row in rows]
    all_pairs = [float(row["all_matched_rmsd_A"]) for row in rows]
    fig, ax = plt.subplots(figsize=(8.3,4.8))
    ax.plot(x,fit,"o-",color=TEAL,lw=2,ms=7,label="RMSD on the fitted subset")
    ax.plot(x,all_pairs,"s--",color=BLUE,lw=2,ms=6,label="RMSD on all 258 pairs after that fit")
    ax.set_xticks(x,[f"pLDDT ≥ {row['min_plddt']}\n{row['fit_residues']} fitted pairs" for row in rows])
    ax.set(ylabel="Cα RMSD (Å)",ylim=(0,.65),xlim=(-.25,2.25))
    ax.set_title("A smaller fitted RMSD can reflect which atoms were selected",loc="left",fontweight="bold",fontsize=14,pad=18)
    ax.grid(axis="y",color=PALE); ax.spines[["top","right"]].set_visible(False)
    for xi,f,a in zip(x,fit,all_pairs):
        ax.annotate(f"{f:.3f}",(xi,f),xytext=(0,-18),textcoords="offset points",ha="center",color=TEAL,fontsize=10)
        ax.annotate(f"{a:.3f}",(xi,a),xytext=(0,9),textcoords="offset points",ha="center",color=BLUE,fontsize=10)
    ax.legend(loc="lower left",frameon=False,fontsize=10)
    fig.text(.12,-.01,"Fixed sensitivity settings; these are descriptive fits to one structure pair, not independent accuracy tests.",color=MUTED,fontsize=9.5)
    save(fig,out,"fit-selection.svg","Fit selection changes the reported structural RMSD",
         "At pLDDT cutoffs zero, 70 and 90, fitted subsets contain 258, 257 and 256 pairs. Subset RMSD falls while the all-pair RMSD stays near 0.53 angstrom. Exact values are retained in fit_sensitivity.csv.",previews)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=ROOT/"docs/figures")
    parser.add_argument("--preview-dir",type=Path)
    args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    mapping_figure(args.output_dir,args.preview_dir);selection_figure(args.output_dir,args.preview_dir)
    sources=["results/residue_comparison.csv","results/fit_sensitivity.csv"]
    record={"scope":"Documentation views of existing computed results; no new structural fitting", "sources":[{"path":p,"sha256":hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in sources],"figures":["residue-mapping.svg","fit-selection.svg"],"command":"python tools/build_documentation_figures.py"}
    (args.output_dir/"provenance.json").write_text(json.dumps(record,indent=2)+"\n")


if __name__ == "__main__":
    main()
