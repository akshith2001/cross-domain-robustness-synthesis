"""Generate the cross-domain RRR spread figure."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from cross_domain_robustness.synthesis import run_synthesis


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary = run_synthesis()
    naive = summary["naive_single_comparison_rrr"]
    alternative = summary["alternative_comparison_rrr"]
    labels = [*naive.keys(), *alternative.keys()]
    naive_y = list(range(len(naive)))
    alternative_y = list(range(len(naive), len(labels)))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(list(naive.values()), naive_y, s=100, color="#1769aa", label="Primary comparison", zorder=3)
    ax.scatter(list(alternative.values()), alternative_y, s=100, color="#b23a2b", marker="D", label="Alternative comparison", zorder=3)
    ax.set_yticks(range(len(labels)), labels, fontsize=8)
    ax.invert_yaxis()
    ax.axvline(1.0, color="#555555", linestyle="--", linewidth=1, label="No degradation")
    ax.axvspan(min(naive.values()), max(naive.values()), color="#1769aa", alpha=0.08)
    ax.set_xlabel("Robustness Retention Ratio")
    ax.set_title("Metric choice changes the apparent cross-domain robustness ranking")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    for extension in ("svg", "png"):
        fig.savefig(args.output_dir / f"cross_domain_rrr_spread.{extension}", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
