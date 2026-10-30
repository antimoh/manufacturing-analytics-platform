# Data Ingestion Module

This module handles data ingestion for the Manufacturing Analytics Platform, providing both local data acquisition and Snowflake loading capabilities.

## Scripts Overview

| Script | Purpose |
|--------|--------|
| `inspect_dataset.py` | Download and profile the UCI dataset |
| `create_manifest.py` | Generate data manifest with checksums |
| `snowflake_loader.py` | Load data to Snowflake programmatically |

## Snowflake Loader

The `snowflake_loader.py` script provides enterprise-grade data ingestion following data engineering best practices:

### Features

- **Secure Credentials**: Uses environment variables (never hardcoded)
- **Idempotent Operations**: Safe to re-run; truncates before loading
- **Comprehensive Logging**: File and console logging with timestamps
- **Data Validation**: Pre-load source validation, post-load Snowflake validation
- **Error Handling**: Meaningful error messages with proper exit codes
- **Two Loading Methods**:
  - `write_pandas()` - Fast pandas integration (default)
  - `load_via_stage()` - Traditional PUT + COPY INTO pattern

### Prerequisites

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Snowflake credentials**:
   
   Copy the example environment file:
   ```bash
   cp ingestion/.env.example .env
   ```
   
   Edit `.env` with your Snowflake credentials:
   ```
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   ```

   Or set environment variables directly:
   
   **Windows (PowerShell)**:
   ```powershell
   $env:SNOWFLAKE_ACCOUNT = "your_account"
   $env:SNOWFLAKE_USER = "your_username"
   $env:SNOWFLAKE_PASSWORD = "your_password"
   ```
   
   **Windows (CMD)**:
   ```cmd
   set SNOWFLAKE_ACCOUNT=your_account
   set SNOWFLAKE_USER=your_username
   set SNOWFLAKE_PASSWORD=your_password
   ```
   
   **Unix/Mac**:
   ```bash
   export SNOWFLAKE_ACCOUNT=your_account
   export SNOWFLAKE_USER=your_username
   export SNOWFLAKE_PASSWORD=your_password
   ```

### Finding Your Snowflake Account Identifier

Your account identifier is visible in the Snowflake URL:
```
https://app.snowflake.com/<org>/<account>/
```

Or run this in Snowflake:
```sql
SELECT CURRENT_ACCOUNT();
```

The format is typically `<account>.<region>` (e.g., `abc12345.us-east-1`).

### Usage

```bash
# From project root
python ingestion/snowflake_loader.py
```

### Expected Output

```
INFO     | Log file: logs/snowflake_load_20261028_143022.log
INFO     | ============================================================
INFO     | Manufacturing Analytics Platform - Snowflake Data Loader
INFO     | ============================================================
INFO     | Loading CSV file: ai4i2020.csv
INFO     | ✓ Loaded 10,000 rows, 14 columns
INFO     | Validating source data...
INFO     | ✓ Row count: 10,000
INFO     | ✓ All 14 expected columns present
INFO     | ✓ No NULL values in source data
INFO     | ✓ Machine types valid: {'L', 'M', 'H'}
INFO     | Connecting to Snowflake account: abc12345.us-east-1
INFO     | ✓ Connected to Snowflake successfully
INFO     | Truncating table MACHINE_SENSOR_DATA for clean load...
INFO     | ✓ Table truncated
INFO     | Loading 10,000 rows to MACHINE_SENSOR_DATA...
INFO     | ✓ Successfully loaded 10,000 rows in 1 chunk(s)
INFO     | Validating loaded data in Snowflake...
INFO     | ✓ Rows in Snowflake: 10,000
INFO     | ✓ Machine failures: 339
INFO     | ✓ Load timestamp: 2026-10-28 14:30:25
INFO     | ✓ Connection closed
INFO     | ============================================================
INFO     | LOAD COMPLETE
INFO     |   Rows loaded:    10,000
INFO     |   Failures found: 339
INFO     |   Duration:       3.42 seconds
INFO     | ============================================================
```

### Logging

Logs are written to:
- Console: INFO level and above
- File: `logs/snowflake_load_<timestamp>.log` (DEBUG level)

### Security Notes

- **Never commit `.env` files** - They're in `.gitignore`
- **Never hardcode credentials** - Always use environment variables
- **Use least-privilege access** - Create a dedicated Snowflake user for loading if possible
- **Rotate credentials regularly** - Update your token/password periodically

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   UCI Dataset   │────▶│  inspect_dataset │────▶│   data/raw/     │
│   (External)    │     │      .py         │     │  ai4i2020.csv   │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                        ┌──────────────────┐              │
                        │  create_manifest │◀─────────────┘
                        │      .py         │              │
                        └──────────────────┘              │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│    Snowflake    │◀────│ snowflake_loader │◀────│  Validated CSV  │
│  RAW.MACHINE_   │     │      .py         │     │                 │
│  SENSOR_DATA    │     └──────────────────┘     └─────────────────┘
└─────────────────┘
```

## Troubleshooting

### "Missing required environment variables"
Set the required environment variables as shown above.

### "snowflake-connector-python not installed"
```bash
pip install snowflake-connector-python[pandas]
```

### "Data file not found"
Ensure you've run `inspect_dataset.py` first to download the data.

### Connection errors
1. Check your account identifier format
2. Verify your username/password
3. Ensure your IP is whitelisted (if using network policies)
4. Check that the warehouse is not suspended
