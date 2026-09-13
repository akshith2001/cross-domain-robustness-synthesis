import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, "../src")
from cross_domain_robustness.synthesis import run_synthesis

summary = run_synthesis()
naive = summary["naive_single_comparison_rrr"]
alt = summary["alternative_comparison_rrr"]

fig, ax = plt.subplots(figsize=(9, 5.5))

y_naive = list(range(len(naive)))
labels_naive = list(naive.keys())
vals_naive = list(naive.values())

y_alt = list(range(len(naive), len(naive) + len(alt)))
labels_alt = list(alt.keys())
vals_alt = list(alt.values())

ax.scatter(vals_naive, y_naive, s=100, color="#2a6fdb", label="Naive single comparison per domain", zorder=3)
ax.scatter(vals_alt, y_alt, s=100, color="#c1440e", marker="D", label="Alternative, equally valid comparison", zorder=3)

all_labels = labels_naive + labels_alt
all_y = y_naive + y_alt
ax.set_yticks(all_y)
ax.set_yticklabels(all_labels, fontsize=8)
ax.invert_yaxis()

ax.axvline(1.0, color="gray", linestyle="--", linewidth=1, label="No degradation (RRR = 1.0)")
ax.axvspan(min(vals_naive), max(vals_naive), color="#2a6fdb", alpha=0.08)

ax.set_xlabel("Robustness Retention Ratio (higher = less degradation under stress)")
ax.set_title(
    "A single robustness metric does not generalise across domains\n"
    "(shaded band = naive comparison's apparent range; red diamonds show how far it moves\n"
    "once an equally defensible alternative comparison is used within the same domain)"
)
ax.legend(fontsize=8, loc="lower right")
fig.tight_layout()
fig.savefig("cross_domain_rrr_spread.svg", format="svg")
fig.savefig("cross_domain_rrr_spread.png", format="png", dpi=120)
print("saved figures")
