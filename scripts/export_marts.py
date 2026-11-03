"""
Export dbt Mart Tables from Snowflake to CSV
=============================================

This script exports the analytics-ready mart tables from Snowflake
to local CSV files for use with Streamlit Community Cloud.

Usage:
    python scripts/export_marts.py

Environment Variables Required:
    SNOWFLAKE_ACCOUNT   - Snowflake account identifier
    SNOWFLAKE_USER      - Snowflake username
"""

import os
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

try:
    import snowflake.connector
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install snowflake-connector-python[pandas] cryptography")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_EXPORT_DIR = PROJECT_ROOT / "streamlit_app" / "data"

# Tables to export from the analytics schema
MART_TABLES = [
    "dim_machine_types",
    "fct_failure_events",
    "fct_failure_summary",
    "fct_machine_performance",
    "fct_predictive_indicators",
]

SNOWFLAKE_CONFIG = {
    "account": os.environ.get("SNOWFLAKE_ACCOUNT", "FYIUUJV-XJ40878"),
    "user": os.environ.get("SNOWFLAKE_USER", "ANTIMOH@GMAIL.COM"),
    "warehouse": "ANALYTICS_WH",
    "database": "MANUFACTURING_ANALYTICS",
    "schema": "RAW_ANALYTICS",  # dbt creates tables with schema prefix
    "role": "ACCOUNTADMIN",
}


# =============================================================================
# AUTHENTICATION
# =============================================================================

def load_private_key():
    """Load the RSA private key for Snowflake authentication."""
    key_path = Path(os.environ.get(
        "SNOWFLAKE_PRIVATE_KEY_PATH",
        Path.home() / ".snowflake" / "rsa_key.p8"
    ))
    
    if not key_path.exists():
        raise FileNotFoundError(f"Private key not found at: {key_path}")
    
    with open(key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    
    # Convert to bytes format required by Snowflake connector
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    return private_key_bytes


def get_snowflake_connection():
    """Create a Snowflake connection using key-pair authentication."""
    print("Connecting to Snowflake...")
    
    private_key_bytes = load_private_key()
    
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_CONFIG["account"],
        user=SNOWFLAKE_CONFIG["user"],
        private_key=private_key_bytes,
        warehouse=SNOWFLAKE_CONFIG["warehouse"],
        database=SNOWFLAKE_CONFIG["database"],
        schema=SNOWFLAKE_CONFIG["schema"],
        role=SNOWFLAKE_CONFIG["role"],
    )
    
    print(f"✓ Connected to {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}")
    return conn


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def export_table(conn, table_name: str, output_dir: Path) -> dict:
    """Export a single table to CSV and return metadata."""
    print(f"\nExporting {table_name}...")
    
    # Query the table
    query = f"SELECT * FROM {table_name}"
    
    cursor = conn.cursor()
    cursor.execute(query)
    
    # Fetch as pandas DataFrame
    df = cursor.fetch_pandas_all()
    
    # Convert column names to lowercase for consistency
    df.columns = [col.lower() for col in df.columns]
    
    # Save to CSV
    output_path = output_dir / f"{table_name}.csv"
    df.to_csv(output_path, index=False)
    
    metadata = {
        "table": table_name,
        "rows": len(df),
        "columns": len(df.columns),
        "file": str(output_path.name),
        "size_kb": round(output_path.stat().st_size / 1024, 1),
    }
    
    print(f"  ✓ {metadata['rows']:,} rows, {metadata['columns']} columns → {output_path.name} ({metadata['size_kb']} KB)")
    
    cursor.close()
    return metadata


def main():
    """Main export function."""
    print("=" * 60)
    print("Snowflake Mart Tables Export")
    print("=" * 60)
    print(f"Export time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target directory: {DATA_EXPORT_DIR}")
    print()
    
    # Create export directory
    DATA_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Connect to Snowflake
    conn = get_snowflake_connection()
    
    # Export each table
    export_metadata = []
    
    try:
        for table_name in MART_TABLES:
            metadata = export_table(conn, table_name, DATA_EXPORT_DIR)
            export_metadata.append(metadata)
    finally:
        conn.close()
        print("\n✓ Snowflake connection closed")
    
    # Summary
    print("\n" + "=" * 60)
    print("Export Summary")
    print("=" * 60)
    
    total_rows = sum(m["rows"] for m in export_metadata)
    total_size = sum(m["size_kb"] for m in export_metadata)
    
    print(f"Tables exported: {len(export_metadata)}")
    print(f"Total rows: {total_rows:,}")
    print(f"Total size: {total_size:.1f} KB")
    print(f"\nFiles saved to: {DATA_EXPORT_DIR}")
    
    # Create a manifest file
    manifest_path = DATA_EXPORT_DIR / "manifest.json"
    import json
    manifest = {
        "exported_at": datetime.now().isoformat(),
        "source_database": SNOWFLAKE_CONFIG["database"],
        "source_schema": SNOWFLAKE_CONFIG["schema"],
        "tables": export_metadata,
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Manifest saved to: {manifest_path}")
    print("\n✓ Export complete!")


if __name__ == "__main__":
    main()
