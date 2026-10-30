"""
Snowflake Data Loader - Manufacturing Analytics Platform
=========================================================

This script provides programmatic data ingestion from local CSV files
to Snowflake, following data engineering best practices:

- Secure credential management via environment variables
- Idempotent operations (safe to re-run)
- Comprehensive logging
- Data validation pre and post load
- Error handling with meaningful messages

Usage:
    python ingestion/snowflake_loader.py

Environment Variables Required:
    SNOWFLAKE_ACCOUNT   - Snowflake account identifier (e.g., 'abc12345.us-east-1')
    SNOWFLAKE_USER      - Snowflake username
    SNOWFLAKE_PASSWORD  - Snowflake password
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
from typing import Optional, Dict, Any

import pandas as pd

try:
    import snowflake.connector
    from snowflake.connector.pandas_tools import write_pandas
except ImportError:
    print("Error: snowflake-connector-python not installed.")
    print("Install with: pip install snowflake-connector-python[pandas]")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
LOG_DIR = PROJECT_ROOT / "logs"

# Default Snowflake configuration
DEFAULT_CONFIG = {
    "warehouse": "ANALYTICS_WH",
    "database": "MANUFACTURING_ANALYTICS",
    "schema": "RAW",
    "table": "MACHINE_SENSOR_DATA",
    "stage": "RAW_DATA_STAGE",
    "file_format": "CSV_FORMAT",
}

# Expected data characteristics for validation
EXPECTED_ROW_COUNT = 10000
EXPECTED_COLUMNS = [
    "UDI", "Product ID", "Type", "Air temperature [K]",
    "Process temperature [K]", "Rotational speed [rpm]",
    "Torque [Nm]", "Tool wear [min]", "Machine failure",
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
    
    # Create logger
    logger = logging.getLogger("snowflake_loader")
    logger.setLevel(logging.DEBUG)
    
    # File handler - detailed logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    
    # Console handler - info and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(levelname)-8s | %(message)s")
    console_handler.setFormatter(console_format)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Log file: {log_file}")
    return logger


# =============================================================================
# SNOWFLAKE CONNECTION
# =============================================================================

def get_snowflake_config() -> Dict[str, str]:
    """
    Load Snowflake configuration from environment variables.
    
    Raises:
        EnvironmentError: If required variables are missing.
    """
    required_vars = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Set these variables before running the script:\n"
            "  Windows:  set SNOWFLAKE_ACCOUNT=your_account\n"
            "  Unix:     export SNOWFLAKE_ACCOUNT=your_account"
        )
    
    return {
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "password": os.environ["SNOWFLAKE_PASSWORD"],
        "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE", DEFAULT_CONFIG["warehouse"]),
        "database": os.environ.get("SNOWFLAKE_DATABASE", DEFAULT_CONFIG["database"]),
        "schema": os.environ.get("SNOWFLAKE_SCHEMA", DEFAULT_CONFIG["schema"]),
    }


def create_connection(config: Dict[str, str], logger: logging.Logger):
    """
    Create and return a Snowflake connection.
    
    Args:
        config: Dictionary with connection parameters.
        logger: Logger instance.
    
    Returns:
        Snowflake connection object.
    """
    logger.info(f"Connecting to Snowflake account: {config['account']}")
    logger.debug(f"Database: {config['database']}, Schema: {config['schema']}")
    
    conn = snowflake.connector.connect(
        account=config["account"],
        user=config["user"],
        password=config["password"],
        warehouse=config["warehouse"],
        database=config["database"],
        schema=config["schema"],
    )
    
    logger.info("✓ Connected to Snowflake successfully")
    return conn


# =============================================================================
# DATA VALIDATION
# =============================================================================

def validate_source_data(df: pd.DataFrame, logger: logging.Logger) -> bool:
    """
    Validate source data before loading.
    
    Args:
        df: Pandas DataFrame with source data.
        logger: Logger instance.
    
    Returns:
        True if validation passes, False otherwise.
    """
    logger.info("Validating source data...")
    is_valid = True
    
    # Check row count
    row_count = len(df)
    if row_count != EXPECTED_ROW_COUNT:
        logger.warning(f"Row count mismatch: expected {EXPECTED_ROW_COUNT}, got {row_count}")
        is_valid = False
    else:
        logger.info(f"✓ Row count: {row_count:,}")
    
    # Check columns
    missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_cols:
        logger.error(f"Missing columns: {missing_cols}")
        is_valid = False
    else:
        logger.info(f"✓ All {len(EXPECTED_COLUMNS)} expected columns present")
    
    # Check for nulls in critical columns
    null_counts = df[EXPECTED_COLUMNS].isnull().sum()
    if null_counts.sum() > 0:
        logger.warning(f"NULL values found:\n{null_counts[null_counts > 0]}")
    else:
        logger.info("✓ No NULL values in source data")
    
    # Check machine types
    valid_types = {"L", "M", "H"}
    actual_types = set(df["Type"].unique())
    if not actual_types.issubset(valid_types):
        logger.error(f"Invalid machine types: {actual_types - valid_types}")
        is_valid = False
    else:
        logger.info(f"✓ Machine types valid: {actual_types}")
    
    return is_valid


def validate_loaded_data(conn, table: str, logger: logging.Logger) -> Dict[str, Any]:
    """
    Validate data after loading to Snowflake.
    
    Args:
        conn: Snowflake connection.
        table: Target table name.
        logger: Logger instance.
    
    Returns:
        Dictionary with validation results.
    """
    logger.info("Validating loaded data in Snowflake...")
    cursor = conn.cursor()
    
    results = {}
    
    # Row count
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    results["row_count"] = cursor.fetchone()[0]
    logger.info(f"✓ Rows in Snowflake: {results['row_count']:,}")
    
    # Failure count
    cursor.execute(f"SELECT SUM(machine_failure) FROM {table}")
    results["failure_count"] = cursor.fetchone()[0]
    logger.info(f"✓ Machine failures: {results['failure_count']}")
    
    # Load timestamp range
    cursor.execute(f"SELECT MIN(_loaded_at), MAX(_loaded_at) FROM {table}")
    min_ts, max_ts = cursor.fetchone()
    results["load_timestamp"] = {"min": min_ts, "max": max_ts}
    logger.info(f"✓ Load timestamp: {max_ts}")
    
    cursor.close()
    return results


# =============================================================================
# DATA LOADING
# =============================================================================

def load_csv_to_dataframe(file_path: Path, logger: logging.Logger) -> pd.DataFrame:
    """
    Load CSV file into a pandas DataFrame.
    
    Args:
        file_path: Path to CSV file.
        logger: Logger instance.
    
    Returns:
        Pandas DataFrame with the data.
    """
    logger.info(f"Loading CSV file: {file_path.name}")
    
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    logger.info(f"✓ Loaded {len(df):,} rows, {len(df.columns)} columns")
    
    return df


def prepare_dataframe_for_snowflake(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """
    Prepare DataFrame for Snowflake loading by renaming columns.
    
    Snowflake column names should be uppercase and use underscores.
    
    Args:
        df: Source DataFrame.
        logger: Logger instance.
    
    Returns:
        DataFrame with Snowflake-compatible column names.
    """
    logger.info("Preparing data for Snowflake...")
    
    # Column mapping from CSV headers to Snowflake columns
    column_mapping = {
        "UDI": "UDI",
        "Product ID": "PRODUCT_ID",
        "Type": "TYPE",
        "Air temperature [K]": "AIR_TEMPERATURE",
        "Process temperature [K]": "PROCESS_TEMPERATURE",
        "Rotational speed [rpm]": "ROTATIONAL_SPEED",
        "Torque [Nm]": "TORQUE",
        "Tool wear [min]": "TOOL_WEAR",
        "Machine failure": "MACHINE_FAILURE",
        "TWF": "TWF",
        "HDF": "HDF",
        "PWF": "PWF",
        "OSF": "OSF",
        "RNF": "RNF",
    }
    
    df_prepared = df.rename(columns=column_mapping)
    logger.info(f"✓ Renamed {len(column_mapping)} columns to Snowflake format")
    
    return df_prepared


def truncate_table(conn, table: str, logger: logging.Logger) -> None:
    """
    Truncate target table before loading (idempotent operation).
    
    Args:
        conn: Snowflake connection.
        table: Table name to truncate.
        logger: Logger instance.
    """
    logger.info(f"Truncating table {table} for clean load...")
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE IF EXISTS {table}")
    cursor.close()
    logger.info("✓ Table truncated")


def load_dataframe_to_snowflake(
    conn,
    df: pd.DataFrame,
    table: str,
    logger: logging.Logger,
    truncate: bool = True
) -> int:
    """
    Load DataFrame to Snowflake table.
    
    Uses Snowflake's optimized write_pandas function for efficient bulk loading.
    
    Args:
        conn: Snowflake connection.
        df: DataFrame to load.
        table: Target table name.
        logger: Logger instance.
        truncate: Whether to truncate table before loading.
    
    Returns:
        Number of rows loaded.
    """
    if truncate:
        truncate_table(conn, table, logger)
    
    logger.info(f"Loading {len(df):,} rows to {table}...")
    
    # Use write_pandas for efficient bulk loading
    success, num_chunks, num_rows, _ = write_pandas(
        conn=conn,
        df=df,
        table_name=table,
        auto_create_table=False,
        quote_identifiers=False,
    )
    
    if success:
        logger.info(f"✓ Successfully loaded {num_rows:,} rows in {num_chunks} chunk(s)")
    else:
        logger.error("Failed to load data to Snowflake")
        raise RuntimeError("Data load failed")
    
    return num_rows


# =============================================================================
# ALTERNATIVE: STAGE-BASED LOADING
# =============================================================================

def load_via_stage(
    conn,
    file_path: Path,
    stage: str,
    table: str,
    file_format: str,
    logger: logging.Logger
) -> int:
    """
    Load data via internal stage using PUT and COPY INTO.
    
    This is the traditional Snowflake loading pattern and useful
    for very large files or when you need more control.
    
    Args:
        conn: Snowflake connection.
        file_path: Local file path.
        stage: Stage name.
        table: Target table name.
        file_format: File format name.
        logger: Logger instance.
    
    Returns:
        Number of rows loaded.
    """
    cursor = conn.cursor()
    
    try:
        # Upload file to stage
        logger.info(f"Uploading {file_path.name} to stage @{stage}...")
        put_sql = f"PUT file://{file_path.as_posix()} @{stage} AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
        cursor.execute(put_sql)
        logger.info("✓ File uploaded to stage")
        
        # Truncate target table
        truncate_table(conn, table, logger)
        
        # Copy data from stage to table
        logger.info(f"Loading data from stage to {table}...")
        copy_sql = f"""
            COPY INTO {table} (
                udi, product_id, type, air_temperature, process_temperature,
                rotational_speed, torque, tool_wear, machine_failure,
                twf, hdf, pwf, osf, rnf
            )
            FROM @{stage}
            FILE_FORMAT = (FORMAT_NAME = '{file_format}')
            ON_ERROR = 'ABORT_STATEMENT'
        """
        cursor.execute(copy_sql)
        
        # Get load results
        result = cursor.fetchone()
        rows_loaded = result[3] if result else 0  # rows_loaded is 4th column
        logger.info(f"✓ Loaded {rows_loaded:,} rows via COPY INTO")
        
        # Clean up stage
        logger.info("Cleaning up staged files...")
        cursor.execute(f"REMOVE @{stage}")
        logger.info("✓ Stage cleaned")
        
        return rows_loaded
        
    finally:
        cursor.close()


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
        # Get configuration
        config = get_snowflake_config()
        
        # Load source data
        csv_file = DATA_DIR / "ai4i2020.csv"
        df = load_csv_to_dataframe(csv_file, logger)
        
        # Validate source data
        if not validate_source_data(df, logger):
            logger.error("Source data validation failed. Aborting.")
            sys.exit(1)
        
        # Prepare data for Snowflake
        df_prepared = prepare_dataframe_for_snowflake(df, logger)
        
        # Connect to Snowflake
        conn = create_connection(config, logger)
        
        try:
            # Load data using pandas integration (faster for this dataset size)
            rows_loaded = load_dataframe_to_snowflake(
                conn=conn,
                df=df_prepared,
                table=DEFAULT_CONFIG["table"],
                logger=logger,
                truncate=True
            )
            
            # Alternative: Load via stage (uncomment to use)
            # rows_loaded = load_via_stage(
            #     conn=conn,
            #     file_path=csv_file,
            #     stage=DEFAULT_CONFIG["stage"],
            #     table=DEFAULT_CONFIG["table"],
            #     file_format=DEFAULT_CONFIG["file_format"],
            #     logger=logger
            # )
            
            # Validate loaded data
            validation_results = validate_loaded_data(
                conn, DEFAULT_CONFIG["table"], logger
            )
            
            # Final validation check
            if validation_results["row_count"] != EXPECTED_ROW_COUNT:
                logger.error(
                    f"Row count mismatch after load: "
                    f"expected {EXPECTED_ROW_COUNT}, got {validation_results['row_count']}"
                )
                sys.exit(1)
            
        finally:
            conn.close()
            logger.info("✓ Connection closed")
        
        # Summary
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
