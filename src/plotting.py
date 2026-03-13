"""
plotting.py
Shared plotting helpers for the HER2 analysis pipeline.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

FIGURES_DIR = Path(__file__).parent.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

# Consistent color palette for HER2 status
HER2_PALETTE = {
    "Positive": "#E74C3C",
    "Negative": "#3498DB",
    "Equivocal": "#F39C12",
    "Indeterminate": "#95A5A6",
    "Unknown": "#BDC3C7",
}


def save_fig(name: str, dpi: int = 150) -> None:
    """Save current figure to figures/ directory."""
    path = FIGURES_DIR / f"{name}.png"
    plt.savefig(path, dpi=dpi, bbox_inches="tight")
    print(f"Saved figure: figures/{name}.png")


def plot_qc_distributions(qc_df: pd.DataFrame, title: str = "QC Summary") -> None:
    """Plot distributions of total counts, detected genes, and median expression."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle(title)

    for ax, col in zip(axes, ["total_counts", "detected_genes", "median_expression"]):
        ax.hist(qc_df[col], bins=50, edgecolor="white", color="#2980B9")
        ax.set_xlabel(col.replace("_", " ").title())
        ax.set_ylabel("Samples")

    plt.tight_layout()


def plot_scatter_2d(coords: pd.DataFrame, hue: pd.Series, title: str,
                    x_label: str = "Component 1", y_label: str = "Component 2") -> None:
    """
    Generic 2D scatter plot (for PCA / UMAP output).
    coords: DataFrame with two columns (x, y)
    hue: Series with category labels aligned to coords index
    """
    df_plot = coords.copy()
    df_plot["hue"] = hue.values

    palette = {k: v for k, v in HER2_PALETTE.items() if k in df_plot["hue"].unique()}

    fig, ax = plt.subplots(figsize=(8, 6))
    for label, group in df_plot.groupby("hue"):
        ax.scatter(group.iloc[:, 0], group.iloc[:, 1],
                   label=label, alpha=0.6, s=20,
                   color=palette.get(label, "#999999"))
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend(title="HER2 Status", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()


def plot_expression_boxplot(df: pd.DataFrame, gene: str, group_col: str,
                             order: list = None, title: str = None) -> None:
    """Boxplot of a gene's expression across groups."""
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=df, x=group_col, y=gene, order=order,
                palette="Set2", ax=ax, fliersize=2)
    ax.set_title(title or f"{gene} expression by {group_col}")
    ax.set_xlabel(group_col)
    ax.set_ylabel(f"{gene} (log2 CPM)")
    plt.tight_layout()
