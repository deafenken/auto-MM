"""Matplotlib RC and palette for stage2_solving figures.

Import this and call apply_style() at the top of every plotting script.

    from src.style import PALETTE, apply_style
    apply_style()
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot(x, y, color=PALETTE[0])
    fig.savefig("figures/fig-name.pdf", bbox_inches="tight", pad_inches=0.05)
"""

PALETTE = [
    "#2E5E8A",  # deep blue
    "#D87A3D",  # rust orange
    "#5A8A3D",  # olive green
    "#8A2E5E",  # plum
    "#3D8A8A",  # teal
    "#8A8A2E",  # mustard
    "#5A2E8A",  # purple-blue — use sparingly
]


def apply_style():
    """Set global rcParams. Idempotent."""
    import matplotlib as mpl

    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif", "serif"],
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 0,          # no in-figure titles by default
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.0,
        "lines.markersize": 4,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
        "pdf.fonttype": 42,            # embed fonts as TrueType (not Type 3)
        "ps.fonttype": 42,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linewidth": 0.5,
        "axes.prop_cycle": mpl.cycler(color=PALETTE),
    })


def chinese_friendly():
    """Call AFTER apply_style() when the paper is Chinese.

    Picks a Chinese font that is installed on most systems. If none is
    available, matplotlib falls back to a default font and you will see
    boxes where Chinese should be — install one of the listed fonts.
    """
    import matplotlib as mpl

    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = [
        "Source Han Sans SC", "Source Han Sans CN",
        "PingFang SC", "Noto Sans CJK SC", "Microsoft YaHei",
        "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans",
    ]
    mpl.rcParams["axes.unicode_minus"] = False


def cm_for_heatmap(diverging=False):
    """Return the recommended colormap name for heatmaps."""
    return "RdBu_r" if diverging else "viridis"
