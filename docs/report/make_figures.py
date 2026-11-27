"""Figures for the course report, from results_ada/final_all/summary_ci.md values (T-Drive test split)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# method: (drivable share, CI, Spearman, CI, itemset Jaccard)
M = {
    "Real test": (1.000, 0, 0.872, 0, 0.603),
    "Markov": (1.000, 0, 0.925, 0.030, 0.509),
    "Independent": (0.058, 0.004, 0.912, 0.025, 0.000),
    "TabDiff default": (0.610, 0.010, 0.814, 0.026, 0.102),
    "TabDiff random 0.1": (0.626, 0.011, 0.809, 0.020, 0.109),
    "TabDiff graph-aware 0.1": (0.870, 0.010, 0.519, 0.063, 0.026),
    "DiffTraj fine-tuned": (0.838, 0.001, 0.622, 0.057, 0.335),
    "DiffTraj scratch": (0.708, 0.018, 0.577, 0.027, 0.024),
}
INK, RUST, GREY = "#1b1d22", "#b5491d", "#8a8a8a"
col = {k: (RUST if k.startswith("TabDiff") else INK if k.startswith("DiffTraj") else GREY) for k in M}
off = {"Real test": (-7, -3, "right"), "Markov": (-6, 4, "right"), "Independent": (6, -3, "left"),
       "TabDiff default": (6, 5, "left"), "TabDiff random 0.1": (6, -10, "left"),
       "TabDiff graph-aware 0.1": (-6, -12, "right"), "DiffTraj fine-tuned": (6, 3, "left"),
       "DiffTraj scratch": (-6, -10, "right")}
plt.rcParams.update({"font.family": "serif", "font.size": 8})
fig, ax = plt.subplots(figsize=(3.4, 2.6))
for k, (v, vc, s, sc, _) in M.items():
    ax.errorbar(v * 100, s, xerr=vc * 100, yerr=sc, fmt="o", ms=4, color=col[k], ecolor=col[k], elinewidth=0.8, capsize=1.5)
    dx, dy, ha = off[k]
    ax.annotate(k, (v * 100, s), textcoords="offset points", xytext=(dx, dy), ha=ha, fontsize=6.5, color=col[k])
ax.set_xlabel("Drivable trips (%)")
ax.set_ylabel("Busy roads: Spearman")
ax.set_xlim(-5, 112); ax.set_ylim(0.45, 0.98)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
fig.savefig("figures/tradeoff.pdf"); fig.savefig("figures/tradeoff.png", dpi=220)

fig, ax = plt.subplots(figsize=(3.4, 2.1))
ks = [k for k in M if k != "Independent"]
ax.barh(range(len(ks)), [M[k][4] for k in ks], color=[col[k] for k in ks], height=0.6)
ax.set_yticks(range(len(ks))); ax.set_yticklabels(ks, fontsize=7); ax.invert_yaxis()
for i, k in enumerate(ks):
    ax.text(M[k][4] + 0.01, i, f"{M[k][4]:.2f}", va="center", fontsize=6.5)
ax.set_xlabel("Itemset Jaccard with real training set")
ax.set_xlim(0, 0.72)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig("figures/itemsets.pdf"); fig.savefig("figures/itemsets.png", dpi=220)
