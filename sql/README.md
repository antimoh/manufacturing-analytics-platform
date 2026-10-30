# SQL Scripts - Manufacturing Analytics Platform

This directory contains the SQL scripts for setting up and managing the Snowflake data warehouse.

## Script Execution Order

Run these scripts in sequence to set up the complete data pipeline:

| Order | Script | Purpose |
|-------|--------|--------|
| 1 | `01_setup_database.sql` | Create database, schemas, and warehouse |
| 2 | `02_create_raw_objects.sql` | Create file format, stage, and raw table |
| 3 | `03_load_raw_data.sql` | Load CSV data from stage into raw table |
| 4 | `04_validate_raw_data.sql` | Run data quality validations |

## Data Architecture

```
                    +-------------------------------------+
                    |   MANUFACTURING_ANALYTICS Database  |
                    +-------------------------------------+
                                     |
          +--------------------------+------------------------+
          |                          |                        |
          v                          v                        v
    +----------+              +----------+              +----------+
    |   RAW    |              | STAGING  |              |ANALYTICS |
    |  Schema  |     -->      |  Schema  |     -->      |  Schema  |
    +----------+              +----------+              +----------+
         |                         |                         |
    Source data              Cleaned &                 Business-ready
    as loaded                standardized               models
```

## Quick Start

### Prerequisites
- Snowflake account with ACCOUNTADMIN privileges
- Local copy of `ai4i2020.csv` dataset

### Step 1: Run Setup Scripts
```sql
-- Run in Snowsight or SnowSQL
-- Execute 01_setup_database.sql
-- Execute 02_create_raw_objects.sql
```

### Step 2: Upload Data File
Using Snowsight UI:
1. Navigate to: Data -> Databases -> MANUFACTURING_ANALYTICS -> RAW -> Stages
2. Select `RAW_DATA_STAGE`
3. Click "Upload files"
4. Select `ai4i2020.csv` from your local machine

Or using SnowSQL:
```bash
snowsql -a <account> -u <user>
PUT file://path/to/ai4i2020.csv @MANUFACTURING_ANALYTICS.RAW.RAW_DATA_STAGE;
```

### Step 3: Load and Validate
```sql
-- Execute 03_load_raw_data.sql
-- Execute 04_validate_raw_data.sql
```

## Objects Created

### Database
- `MANUFACTURING_ANALYTICS` - Main project database

### Schemas
- `RAW` - Source data as loaded from external sources
- `STAGING` - Cleaned and standardized data (future)
- `ANALYTICS` - Business-ready models (future)

### Warehouse
- `ANALYTICS_WH` - X-SMALL, auto-suspend 60s, auto-resume enabled

### Raw Layer Objects
- `CSV_FORMAT` - File format for CSV parsing
- `RAW_DATA_STAGE` - Internal stage for file uploads
- `MACHINE_SENSOR_DATA` - Raw table for sensor data

## Data Quality Validations

The `04_validate_raw_data.sql` script performs these checks:

| Check | Description | Expected |
|-------|-------------|---------|
| Row Count | Total records loaded | 10,000 |
| Duplicates | No exact duplicate rows | 0 duplicates |
| NULL Values | No NULLs in required columns | 0 NULLs |
| Binary Values | Failure columns contain 0/1 only | Valid |
| Machine Types | Only L, M, H values | Valid |
| Failure Count | Total machine failures | 339 |
| Failure Consistency | Deterministic failures imply machine_failure=1 | Pass |

## Cost Management

The warehouse is configured for minimal credit usage:
- **Size**: X-SMALL (1 credit/hour when running)
- **Auto-suspend**: 60 seconds
- **Auto-resume**: Enabled

To manually suspend the warehouse:
```sql
ALTER WAREHOUSE ANALYTICS_WH SUSPEND;
```

## Troubleshooting

### Warehouse Not Starting
```sql
ALTER WAREHOUSE ANALYTICS_WH RESUME;
```

### File Not Found in Stage
```sql
LIST @MANUFACTURING_ANALYTICS.RAW.RAW_DATA_STAGE;
```

### Permission Issues
Ensure you're using the ACCOUNTADMIN role:
```sql
USE ROLE ACCOUNTADMIN;
```
