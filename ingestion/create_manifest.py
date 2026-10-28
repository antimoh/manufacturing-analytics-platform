"""
Manifest Creation Script
Creates a manifest file with metadata about the raw dataset.

Calculates SHA-256 checksum and records dataset properties for
reproducibility and data lineage tracking.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATA_FILE = RAW_DATA_DIR / "ai4i2020.csv"
MANIFEST_FILE = RAW_DATA_DIR / "manifest.json"


def calculate_sha256(file_path):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def create_manifest(data_file, output_file):
    """Create a manifest file with dataset metadata."""
    if not data_file.exists():
        raise FileNotFoundError(
            f"Data file not found: {data_file}\n"
            "Run inspect_dataset.py first to download the dataset."
        )
    
    # Read dataset
    df = pd.read_csv(data_file)
    
    # Calculate checksum
    checksum = calculate_sha256(data_file)
    
    # Build manifest
    manifest = {
        "file_name": data_file.name,
        "sha256_checksum": checksum,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": df.columns.tolist(),
        "missing_value_count": int(df.isnull().sum().sum()),
        "source": {
            "name": "UCI AI4I 2020 Predictive Maintenance Dataset",
            "url": "https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset",
            "doi": "https://doi.org/10.24432/C5HS5C",
            "license": "CC BY 4.0"
        },
        "ingestion_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Write manifest
    with open(output_file, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Manifest created: {output_file}")
    print(json.dumps(manifest, indent=2))
    
    return manifest


def main():
    """Main execution function."""
    create_manifest(DATA_FILE, MANIFEST_FILE)


if __name__ == "__main__":
    main()
