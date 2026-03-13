"""
data_utils.py
Utilities for loading, merging, and cleaning TCGA BRCA datasets.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
PROCESSED_DIR = Path(__file__).parent.parent / "processed"


def load_rna(path=None) -> pd.DataFrame:
    """Load raw RNA-Seq RSEM counts."""
    path = path or DATA_DIR / "tcga.brca.rsem.csv"
    return pd.read_csv(path, index_col=0)


def load_copy_number(path=None) -> pd.DataFrame:
    """Load ERBB2 copy number data."""
    path = path or DATA_DIR / "brca_tcga_erbb2_copy_number.csv"
    return pd.read_csv(path, index_col=0)


def load_clinical(path=None) -> pd.DataFrame:
    """Load clinical data."""
    path = path or DATA_DIR / "brca_tcga_clinical_data.csv"
    return pd.read_csv(path, index_col=0)


def load_processed(name: str) -> pd.DataFrame:
    """Load a processed parquet file by name (without extension)."""
    return pd.read_parquet(PROCESSED_DIR / f"{name}.parquet")


def save_processed(df: pd.DataFrame, name: str) -> None:
    """Save a DataFrame to processed/ as parquet."""
    PROCESSED_DIR.mkdir(exist_ok=True)
    df.to_parquet(PROCESSED_DIR / f"{name}.parquet")
    print(f"Saved: processed/{name}.parquet  ({df.shape[0]} rows x {df.shape[1]} cols)")


def merge_datasets(rna_norm: pd.DataFrame, cn: pd.DataFrame, clinical: pd.DataFrame) -> pd.DataFrame:
    """
    Merge normalized RNA, copy number, and clinical data on sample/patient ID.
    Returns a merged DataFrame with samples as rows.
    """
    merged = rna_norm.join(cn, how="left", rsuffix="_cn")
    merged = merged.join(clinical, how="left", rsuffix="_clin")
    return merged
