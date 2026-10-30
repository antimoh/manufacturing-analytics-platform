# Data Ingestion Module

This module handles data ingestion for the Manufacturing Analytics Platform, providing both local data acquisition and Snowflake loading capabilities.

## Scripts Overview

| Script | Purpose |
|--------|--------|
| `inspect_dataset.py` | Download and profile the UCI dataset |
| `create_manifest.py` | Generate data manifest with checksums |
| `generate_keys.py` | Generate RSA key pair for Snowflake authentication |
| `snowflake_loader.py` | Load data to Snowflake programmatically |

## Snowflake Loader

The `snowflake_loader.py` script provides enterprise-grade data ingestion following data engineering best practices:

### Features

- **Key-Pair Authentication**: Secure, password-less RSA authentication
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

2. **Set up key-pair authentication** (recommended):
   
   Key-pair authentication is the enterprise-standard approach for automated pipelines:
   
   ```bash
   # Generate RSA key pair
   python ingestion/generate_keys.py
   ```
   
   This creates:
   - `~/.snowflake/rsa_key.p8` (private key - keep secure!)
   - `~/.snowflake/rsa_key.pub` (public key)
   
   The script outputs SQL to register your public key in Snowflake:
   ```sql
   USE ROLE ACCOUNTADMIN;
   ALTER USER "<your_username>" SET RSA_PUBLIC_KEY = '<key_content>';
   ```

3. **Configure environment variables**:
   
   Copy the example environment file:
   ```bash
   cp ingestion/.env.example .env
   ```
   
   Edit `.env` with your Snowflake settings:
   ```
   SNOWFLAKE_ACCOUNT=<org>-<account>
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PRIVATE_KEY_PATH=~/.snowflake/rsa_key.p8
   ```

   Or set environment variables directly:
   
   **Windows (PowerShell)**:
   ```powershell
   $env:SNOWFLAKE_ACCOUNT = "ORGID-ACCOUNTID"
   $env:SNOWFLAKE_USER = "your_username"
   $env:SNOWFLAKE_PRIVATE_KEY_PATH = "$env:USERPROFILE\.snowflake\rsa_key.p8"
   ```
   
   **Unix/Mac**:
   ```bash
   export SNOWFLAKE_ACCOUNT="ORGID-ACCOUNTID"
   export SNOWFLAKE_USER="your_username"
   export SNOWFLAKE_PRIVATE_KEY_PATH="~/.snowflake/rsa_key.p8"
   ```

### Finding Your Snowflake Account Identifier

Your account identifier format is `<org>-<account>`. Find it by running this in Snowflake:
```sql
SELECT CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME();
```

Or check your Snowflake URL:
```
https://app.snowflake.com/<org>/<account>/
```

Example: If your URL is `https://app.snowflake.com/FYIUUJV/XJ40878/`, your account is `FYIUUJV-XJ40878`.

### Finding Your Username (SSO Users)

If you signed up with Google/SSO, your username may be your email address. Verify with:
```sql
SELECT CURRENT_USER();
-- or
SHOW USERS;
```

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
INFO     | ✓ Loaded 10,000 rows, 12 columns
INFO     | Validating source data...
INFO     | ✓ Row count: 10,000
INFO     | ✓ All 12 expected columns present
INFO     | ✓ No NULL values in source data
INFO     | ✓ Machine types valid: {'L', 'M', 'H'}
INFO     | Connecting to Snowflake account: FYIUUJV-XJ40878
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
INFO     |   Duration:       4.99 seconds
INFO     | ============================================================
```

### Logging

Logs are written to:
- Console: INFO level and above
- File: `logs/snowflake_load_<timestamp>.log` (DEBUG level)

Log files are gitignored and should not be committed.

### Security Best Practices

- **Never commit private keys** - `~/.snowflake/` is outside the repo
- **Never commit `.env` files** - They're in `.gitignore`
- **Use key-pair auth** - More secure than password auth for automation
- **Use least-privilege access** - Create a dedicated Snowflake user for loading if possible
- **Rotate keys periodically** - Generate new keys and update Snowflake regularly

## Authentication Methods

### Key-Pair Authentication (Recommended)

Key-pair authentication uses RSA public/private keys:

1. **Generate keys**: `python ingestion/generate_keys.py`
2. **Register public key** in Snowflake (requires ACCOUNTADMIN)
3. **Store private key** securely at `~/.snowflake/rsa_key.p8`
4. **Set environment variable**: `SNOWFLAKE_PRIVATE_KEY_PATH`

Benefits:
- No password storage needed
- Standard for CI/CD and automated pipelines
- Keys can be rotated without changing code
- More secure than password authentication

### Password Authentication (Alternative)

For development/testing, you can use password authentication:

```
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
```

Note: The loader automatically uses key-pair auth if `SNOWFLAKE_PRIVATE_KEY_PATH` is set; otherwise falls back to password auth.

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
          │
          │ Uses key-pair auth
          │ (~/.snowflake/rsa_key.p8)
          ▼
    ┌──────────────────┐
    │  generate_keys   │
    │      .py         │
    └──────────────────┘
```

## Troubleshooting

### "Missing required environment variables"
Ensure these are set:
- `SNOWFLAKE_ACCOUNT` - Format: `ORG-ACCOUNT` (e.g., `FYIUUJV-XJ40878`)
- `SNOWFLAKE_USER` - Your username (may be email for SSO users)
- `SNOWFLAKE_PRIVATE_KEY_PATH` or `SNOWFLAKE_PASSWORD`

### "JWT token is invalid"
Key-pair auth issues:
1. Verify private key path is correct
2. Ensure public key is registered in Snowflake
3. Check username matches exactly (case-sensitive)
4. Try regenerating keys with `generate_keys.py`

### "User does not exist"
For SSO users, the username is often the email address:
```sql
SHOW USERS;  -- Check the LOGIN_NAME column
```

### "snowflake-connector-python not installed"
```bash
pip install snowflake-connector-python[pandas]
```

### "Data file not found"
Ensure you've run `inspect_dataset.py` first to download the data:
```bash
python ingestion/inspect_dataset.py
```

### Connection errors
1. Check your account identifier format (`ORG-ACCOUNT`)
2. Verify your username (may be email for SSO)
3. Ensure your IP is whitelisted (if using network policies)
4. Check that the warehouse is not suspended
