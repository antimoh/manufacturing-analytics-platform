"""
Dataset Inspection Script
Downloads UCI AI4I 2020 Predictive Maintenance Dataset and profiles it.

Source: https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset
DOI: https://doi.org/10.24432/C5HS5C
License: CC BY 4.0
"""

import os
from pathlib import Path

import pandas as pd
from ucimlrepo import fetch_ucirepo

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DATA_DIR / "ai4i2020.csv"


def fetch_dataset():
    """Fetch the UCI AI4I 2020 Predictive Maintenance Dataset."""
    print("Fetching UCI AI4I 2020 Predictive Maintenance Dataset...")
    dataset = fetch_ucirepo(id=601)
    return dataset


def combine_features_targets(dataset):
    """Combine features and targets into a single DataFrame."""
    features = dataset.data.features
    targets = dataset.data.targets
    df = pd.concat([features, targets], axis=1)
    return df


def profile_dataset(df):
    """Print a data profile summary."""
    print("\n" + "=" * 60)
    print("DATASET PROFILE")
    print("=" * 60)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(f"Exact duplicate rows: {df.duplicated().sum()}")
    
    if "Machine failure" in df.columns:
        failures = df["Machine failure"].sum()
        non_failures = len(df) - failures
        failure_rate = failures / len(df) * 100
        print(f"Machine failures: {failures:,}")
        print(f"Non-failures: {non_failures:,}")
        print(f"Failure rate: {failure_rate:.2f}%")
    
    if "Type" in df.columns:
        print(f"Machine type values: {df['Type'].nunique()}")
    
    print("\nColumns:")
    for col in df.columns:
        print(f"  - {col}")
    
    print("\nData types:")
    print(df.dtypes.to_string())
    
    print("\nFirst 5 rows:")
    print(df.head().to_string())
    print("=" * 60)


def save_dataset(df, output_path):
    """Save the dataset to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\nDataset saved to: {output_path}")


def main():
    """Main execution function."""
    dataset = fetch_dataset()
    df = combine_features_targets(dataset)
    profile_dataset(df)
    save_dataset(df, OUTPUT_FILE)
    print("\nIngestion complete.")


if __name__ == "__main__":
    main()
