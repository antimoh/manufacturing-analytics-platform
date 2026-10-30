"""
Snowflake Data Loader - Manufacturing Analytics Platform
=========================================================

This script provides programmatic data ingestion from local CSV files
to Snowflake, following data engineering best practices:

- Secure credential management via key-pair authentication
- Idempotent operations (safe to re-run)
- Comprehensive logging
- Data validation pre and post load
- Error handling with meaningful messages

Usage:
    python ingestion/snowflake_loader.py

Authentication:
    Uses RSA key-pair authentication (more secure than passwords).
    Private key should be stored at: ~/.snowflake/rsa_key.p8
    
Environment Variables Required:
    SNOWFLAKE_ACCOUNT   - Snowflake account identifier (e.g., 'ORGNAME-ACCOUNTNAME')
    SNOWFLAKE_USER      - Snowflake LOGIN_NAME (often email for SSO users)

Environment Variables Optional:
    SNOWFLAKE_PRIVATE_KEY_PATH - Path to private key (default: ~/.snowflake/rsa_key.p8)
    SNOWFLAKE_WAREHOUSE - Warehouse name (default: ANALYTICS_WH)
    SNOWFLAKE_DATABASE  - Database name (default: MANUFACTURING_ANALYTICS)
    SNOWFLAKE_SCHEMA    - Schema name (default: RAW)

Author: Anton Timokhin
Created: 2026-10-28
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

import pandas as pd

try:
    import snowflake.connector
    from snowflake.connector.pandas_tools import write_pandas
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
DATA_DIR = PROJECT_ROOT / "data" / "raw"
LOG_DIR = PROJECT_ROOT / "logs"

DEFAULT_CONFIG = {
    "warehouse": "ANALYTICS_WH",
    "database": "MANUFACTURING_ANALYTICS",
    "schema": "RAW",
    "table": "MACHINE_SENSOR_DATA",
}

EXPECTED_ROW_COUNT = 10000
EXPECTED_COLUMNS = [
    "Type", "Air temperature", "Process temperature", "Rotational speed",
    "Torque", "Tool wear", "Machine failure",
    "TWF", "HDF", "PWF", "OSF", "RNF"
]


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging() -> logging.Logger:
    """Configure logging with both file and console output."""
    LOG_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"snowflake_load_{timestamp}.log"
    
    logger = logging.getLogger("snowflake_loader")
    logger.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(levelname)-8s | %(message)s")
    console_handler.setFormatter(console_format)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Log file: {log_file}")
    return logger


# =============================================================================
# SNOWFLAKE CONNECTION (KEY-PAIR AUTHENTICATION)
# =============================================================================

def load_private_key(key_path: Path):
    """Load RSA private key from file."""
    with open(key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )


def get_snowflake_config(logger: logging.Logger) -> Dict[str, Any]:
    """Load Snowflake configuration from environment variables."""
    required_vars = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Set these variables before running:\n"
            "  $env:SNOWFLAKE_ACCOUNT = 'ORGNAME-ACCOUNTNAME'\n"
            "  $env:SNOWFLAKE_USER = 'your_login_name'"
        )
    
    default_key_path = Path.home() / ".snowflake" / "rsa_key.p8"
    key_path = Path(os.environ.get("SNOWFLAKE_PRIVATE_KEY_PATH", default_key_path))
    
    if not key_path.exists():
        raise FileNotFoundError(
            f"Private key not found at: {key_path}\n"
            "Generate a key pair with: python ingestion/generate_keys.py"
        )
    
    logger.info(f"Loading private key from: {key_path}")
    
    return {
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "private_key": load_private_key(key_path),
        "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE", DEFAULT_CONFIG["warehouse"]),
        "database": os.environ.get("SNOWFLAKE_DATABASE", DEFAULT_CONFIG["database"]),
        "schema": os.environ.get("SNOWFLAKE_SCHEMA", DEFAULT_CONFIG["schema"]),
    }


def create_connection(config: Dict[str, Any], logger: logging.Logger):
    """Create Snowflake connection using key-pair authentication."""
    logger.info(f"Connecting to Snowflake account: {config['account']}")
    logger.info(f"User: {config['user']}")
    
    conn = snowflake.connector.connect(
        account=config["account"],
        user=config["user"],
        private_key=config["private_key"],
        warehouse=config["warehouse"],
        database=config["database"],
        schema=config["schema"],
    )
    
    logger.info("[OK] Connected to Snowflake (key-pair auth)")
    return conn


# =============================================================================
# DATA VALIDATION
# =============================================================================

def validate_source_data(df: pd.DataFrame, logger: logging.Logger) -> bool:
    """Validate source data before loading."""
    logger.info("Validating source data...")
    is_valid = True
    
    row_count = len(df)
    if row_count != EXPECTED_ROW_COUNT:
        logger.warning(f"Row count mismatch: expected {EXPECTED_ROW_COUNT}, got {row_count}")
        is_valid = False
    else:
        logger.info(f"[OK] Row count: {row_count:,}")
    
    missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_cols:
        logger.error(f"Missing columns: {missing_cols}")
        is_valid = False
    else:
        logger.info(f"[OK] All {len(EXPECTED_COLUMNS)} expected columns present")
    
    null_counts = df[EXPECTED_COLUMNS].isnull().sum()
    if null_counts.sum() > 0:
        logger.warning(f"NULL values found:\n{null_counts[null_counts > 0]}")
    else:
        logger.info("[OK] No NULL values in source data")
    
    valid_types = {"L", "M", "H"}
    actual_types = set(df["Type"].unique())
    if not actual_types.issubset(valid_types):
        logger.error(f"Invalid machine types: {actual_types - valid_types}")
        is_valid = False
    else:
        logger.info(f"[OK] Machine types valid: {actual_types}")
    
    return is_valid


def validate_loaded_data(conn, table: str, logger: logging.Logger) -> Dict[str, Any]:
    """Validate data after loading to Snowflake."""
    logger.info("Validating loaded data in Snowflake...")
    cursor = conn.cursor()
    
    results = {}
    
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    results["row_count"] = cursor.fetchone()[0]
    logger.info(f"[OK] Rows in Snowflake: {results['row_count']:,}")
    
    cursor.execute(f"SELECT SUM(machine_failure) FROM {table}")
    results["failure_count"] = cursor.fetchone()[0]
    logger.info(f"[OK] Machine failures: {results['failure_count']}")
    
    cursor.execute(f"SELECT MIN(_loaded_at), MAX(_loaded_at) FROM {table}")
    min_ts, max_ts = cursor.fetchone()
    results["load_timestamp"] = {"min": min_ts, "max": max_ts}
    logger.info(f"[OK] Load timestamp: {max_ts}")
    
    cursor.close()
    return results


# =============================================================================
# DATA LOADING
# =============================================================================

def load_csv_to_dataframe(file_path: Path, logger: logging.Logger) -> pd.DataFrame:
    """Load CSV file into a pandas DataFrame."""
    logger.info(f"Loading CSV file: {file_path.name}")
    
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    logger.info(f"[OK] Loaded {len(df):,} rows, {len(df.columns)} columns")
    
    return df


def prepare_dataframe_for_snowflake(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """Prepare DataFrame for Snowflake loading by renaming columns."""
    logger.info("Preparing data for Snowflake...")
    
    column_mapping = {
        "Type": "TYPE",
        "Air temperature": "AIR_TEMPERATURE",
        "Process temperature": "PROCESS_TEMPERATURE",
        "Rotational speed": "ROTATIONAL_SPEED",
        "Torque": "TORQUE",
        "Tool wear": "TOOL_WEAR",
        "Machine failure": "MACHINE_FAILURE",
        "TWF": "TWF",
        "HDF": "HDF",
        "PWF": "PWF",
        "OSF": "OSF",
        "RNF": "RNF",
    }
    
    df_prepared = df.rename(columns=column_mapping)
    logger.info(f"[OK] Renamed {len(column_mapping)} columns to Snowflake format")
    
    return df_prepared


def truncate_table(conn, table: str, logger: logging.Logger) -> None:
    """Truncate target table before loading."""
    logger.info(f"Truncating table {table} for clean load...")
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE IF EXISTS {table}")
    cursor.close()
    logger.info("[OK] Table truncated")


def load_dataframe_to_snowflake(
    conn,
    df: pd.DataFrame,
    table: str,
    logger: logging.Logger,
    truncate: bool = True
) -> int:
    """Load DataFrame to Snowflake table using write_pandas."""
    if truncate:
        truncate_table(conn, table, logger)
    
    logger.info(f"Loading {len(df):,} rows to {table}...")
    
    success, num_chunks, num_rows, _ = write_pandas(
        conn=conn,
        df=df,
        table_name=table,
        auto_create_table=False,
        quote_identifiers=True,
    )
    
    if success:
        logger.info(f"[OK] Successfully loaded {num_rows:,} rows in {num_chunks} chunk(s)")
    else:
        logger.error("Failed to load data to Snowflake")
        raise RuntimeError("Data load failed")
    
    return num_rows


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function."""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Manufacturing Analytics Platform - Snowflake Data Loader")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    
    try:
        config = get_snowflake_config(logger)
        
        csv_file = DATA_DIR / "ai4i2020.csv"
        df = load_csv_to_dataframe(csv_file, logger)
        
        if not validate_source_data(df, logger):
            logger.error("Source data validation failed. Aborting.")
            sys.exit(1)
        
        df_prepared = prepare_dataframe_for_snowflake(df, logger)
        
        conn = create_connection(config, logger)
        
        try:
            rows_loaded = load_dataframe_to_snowflake(
                conn=conn,
                df=df_prepared,
                table=DEFAULT_CONFIG["table"],
                logger=logger,
                truncate=True
            )
            
            validation_results = validate_loaded_data(
                conn, DEFAULT_CONFIG["table"], logger
            )
            
            if validation_results["row_count"] != EXPECTED_ROW_COUNT:
                logger.error(
                    f"Row count mismatch after load: "
                    f"expected {EXPECTED_ROW_COUNT}, got {validation_results['row_count']}"
                )
                sys.exit(1)
            
        finally:
            conn.close()
            logger.info("[OK] Connection closed")
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info("=" * 60)
        logger.info("LOAD COMPLETE")
        logger.info(f"  Rows loaded:    {rows_loaded:,}")
        logger.info(f"  Failures found: {validation_results['failure_count']}")
        logger.info(f"  Duration:       {duration:.2f} seconds")
        logger.info("=" * 60)
        
    except EnvironmentError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)
    except snowflake.connector.errors.DatabaseError as e:
        logger.error(f"Snowflake error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
