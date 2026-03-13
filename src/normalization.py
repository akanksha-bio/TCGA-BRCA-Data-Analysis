"""
normalization.py
RNA-Seq QC and normalization utilities.
"""

import numpy as np
import pandas as pd


def deseq2_size_factors(counts: pd.DataFrame) -> pd.Series:
    """
    Compute DESeq2-style median-of-ratios size factors.

    Algorithm:
      1. For each gene, compute its geometric mean across all samples
         (genes with zero geometric mean are excluded).
      2. For each sample, divide each count by the gene's geometric mean
         to get per-gene ratios.
      3. The size factor for a sample is the median of its gene ratios.

    Parameters
    ----------
    counts : pd.DataFrame
        Raw count matrix, shape (samples x genes). Must not contain
        metadata columns — pass only numeric gene columns.

    Returns
    -------
    pd.Series
        Size factor per sample (index matches counts.index).
    """
    log_counts = np.log(counts.replace(0, np.nan))          # zeros → NaN, excluded from geo mean
    log_geo_means = log_counts.mean(axis=0)                   # gene-wise log geometric mean
    valid_genes = log_geo_means.notna() & np.isfinite(log_geo_means)
    log_counts_valid = log_counts.loc[:, valid_genes]
    log_geo_means_valid = log_geo_means[valid_genes]

    # Per-sample ratios: log(count) - log(geo_mean) = log(count / geo_mean)
    log_ratios = log_counts_valid.subtract(log_geo_means_valid, axis=1)

    # Size factor = median ratio (ignoring NaN genes)
    size_factors = np.exp(log_ratios.median(axis=1))

    n_genes_used = valid_genes.sum()
    print(f"Size factors computed using {n_genes_used} genes (non-zero geometric mean).")
    print(f"Size factor range: [{size_factors.min():.3f}, {size_factors.max():.3f}]")
    return size_factors


def normalize_deseq2(df: pd.DataFrame, gene_cols: list = None) -> pd.DataFrame:
    """
    Normalize counts using DESeq2-style median-of-ratios size factors.

    Divides each sample's raw counts by its size factor, producing
    composition-bias-corrected normalized counts suitable for log
    transformation and downstream visualization / clustering.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with optional 'sample_type' metadata column and gene count columns.
    gene_cols : list, optional
        Gene columns to normalize. Inferred automatically if not provided.

    Returns
    -------
    pd.DataFrame
        Normalized count DataFrame with the same structure as input.
    """
    meta_cols = [c for c in df.columns if c == "sample_type"]
    gene_cols = gene_cols or [c for c in df.columns if c not in meta_cols]

    counts = df[gene_cols]
    size_factors = deseq2_size_factors(counts)

    normalized = counts.div(size_factors, axis=0)

    result = df[meta_cols].copy()
    result = pd.concat([result, normalized], axis=1)
    return result, size_factors


def filter_low_expression(df: pd.DataFrame, min_counts: float = 1.0, min_samples_frac: float = 0.1) -> pd.DataFrame:
    """
    Remove genes expressed (counts > min_counts) in fewer than min_samples_frac of samples.
    """
    gene_cols = [c for c in df.columns if c != "sample_type" and c != "bcr_patient_barcode"]
    mask = (df[gene_cols] > min_counts).mean(axis=0) >= min_samples_frac
    kept = mask[mask].index.tolist()
    print(f"Genes before filtering: {len(gene_cols)}  |  after: {len(kept)}")
    return df[["sample_type"] + kept] if "sample_type" in df.columns else df[kept]


def normalize_deseq2_pkg(df: pd.DataFrame, condition_col: str = "sample_type") -> tuple[pd.DataFrame, pd.Series]:
    """
    Normalize using pydeseq2's official size-factor estimation (DeseqDataSet).

    Unlike the custom deseq2_size_factors(), pydeseq2:
      - Requires integer counts (rounds floats automatically here)
      - Needs a condition/design column for the GLM model
      - Performs iterative outlier-robust size factor refinement

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with gene count columns and a condition column.
    condition_col : str
        Metadata column used as the design factor (e.g. 'sample_type').

    Returns
    -------
    (normalized_df, size_factors) : tuple
        normalized_df has the same structure as input (condition column preserved).
        size_factors is a pd.Series indexed by sample.
    """
    from pydeseq2.dds import DeseqDataSet

    meta_cols = [c for c in [condition_col, "bcr_patient_barcode"] if c in df.columns]
    gene_cols = [c for c in df.columns if c not in meta_cols]

    # pydeseq2 requires integer counts
    counts_int = df[gene_cols].round().astype(int)
    metadata = df[meta_cols] if meta_cols else pd.DataFrame(
        {"condition": "unknown"}, index=df.index
    )
    if condition_col not in metadata.columns:
        metadata[condition_col] = "unknown"

    # pydeseq2 GLM requires >= 2 levels in the design factor; fall back to a
    # dummy two-level column if the real one is constant.
    if metadata[condition_col].nunique() < 2:
        metadata = metadata.copy()
        metadata[condition_col] = pd.Categorical(
            ["A"] * (len(metadata) // 2) + ["B"] * (len(metadata) - len(metadata) // 2)
        )

    dds = DeseqDataSet(
        counts=counts_int,
        metadata=metadata,
        design_factors=condition_col,
    )
    dds.fit_size_factors()

    # size factors are stored as per-sample scalars in obs, not obsm
    size_factors = pd.Series(dds.obs["size_factors"].values, index=df.index, name="size_factor")
    normalized = counts_int.div(size_factors, axis=0)

    result = df[meta_cols].copy() if meta_cols else pd.DataFrame(index=df.index)
    result = pd.concat([result, normalized], axis=1)
    return result, size_factors


def normalize_tpm(df: pd.DataFrame, gene_cols: list = None) -> pd.DataFrame:
    """
    Normalize by total read depth (CPM-style): counts / sum * 1e6.
    Operates only on numeric gene columns.
    """
    meta_cols = [c for c in df.columns if c == "sample_type"]
    gene_cols = gene_cols or [c for c in df.columns if c not in meta_cols]

    counts = df[gene_cols]
    depth = counts.sum(axis=1)
    normalized = counts.div(depth, axis=0) * 1e6

    result = df[meta_cols].copy()
    result = pd.concat([result, normalized], axis=1)
    return result


def log_transform(df: pd.DataFrame, gene_cols: list = None, pseudocount: float = 1.0) -> pd.DataFrame:
    """
    Apply log2(x + pseudocount) transformation to gene columns.
    """
    meta_cols = [c for c in df.columns if c == "sample_type"]
    gene_cols = gene_cols or [c for c in df.columns if c not in meta_cols]

    result = df[meta_cols].copy()
    result = pd.concat([result, np.log2(df[gene_cols] + pseudocount)], axis=1)
    return result


def qc_summary(df: pd.DataFrame, gene_cols: list = None) -> pd.DataFrame:
    """
    Return a per-sample QC summary: total counts, detected genes, median expression.
    """
    gene_cols = gene_cols or [c for c in df.columns if c != "sample_type"]
    counts = df[gene_cols]
    summary = pd.DataFrame({
        "total_counts": counts.sum(axis=1),
        "detected_genes": (counts > 0).sum(axis=1),
        "median_expression": counts.median(axis=1),
    })
    return summary
