# Tempus HER2 Analysis — TCGA BRCA

Analysis of HER2/ERBB2 in TCGA breast cancer data to assess NGS-based HER2+ patient identification.

## Setup

```bash
pip install -r requirements.txt
```

## Project Structure

```
project1/
├── data/           # Raw input data (read-only)
├── processed/      # Intermediate parquet outputs
├── notebooks/      # Analysis notebooks (run in order)
├── figures/        # Saved plots
├── results/        # Summary tables, model outputs
├── src/            # Shared helper modules
└── writeup/        # Final report
```

## Notebooks (run in order)

| Notebook | Task |
|---|---|
| `01_qc_normalization.ipynb` | QC and normalize RNA-Seq RSEM counts |
| `02_her2_clinical_identification.ipynb` | Identify HER2+ patients from IHC/FISH |
| `03_clustering.ipynb` | PCA + UMAP clustering, HER2 overlay |
| `04_rna_dna_correlation.ipynb` | RNA vs copy number predictive comparison |
| `05_exploratory.ipynb` | Differential expression, TNBC, clinical correlates |

## Data

- `tcga.brca.rsem.csv` — RNA-Seq RSEM counts with `sample_type` column
- `brca_tcga_erbb2_copy_number.csv` — ERBB2 copy number (−2 to +2)
- `brca_tcga_clinical_data.csv` — Clinical data including IHC-HER2, FISH
