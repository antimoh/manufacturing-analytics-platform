/*
================================================================================
Manufacturing Analytics Platform - Data Loading Script
================================================================================
Purpose: Load data from staged CSV file into the raw table.
         This script documents the complete data loading pipeline.

Author: Anton Timokhin
Created: 2026-10-28

Data Source:
    UCI AI4I 2020 Predictive Maintenance Dataset
    - Rows: 10,000
    - Columns: 12
    - Failure Rate: 3.39% (339 failures)

Prerequisites:
    1. Run 01_setup_database.sql
    2. Run 02_create_raw_objects.sql
    3. Upload CSV file to stage using:
       
       Using Snowsight UI:
         - Go to Data -> Databases -> MANUFACTURING_ANALYTICS -> RAW -> Stages
         - Click RAW_DATA_STAGE -> Upload files -> Select ai4i2020.csv
       
       Or using SnowSQL:
         PUT file://path/to/ai4i2020.csv @MANUFACTURING_ANALYTICS.RAW.RAW_DATA_STAGE;

Usage:
    Run this script after uploading the CSV file to the stage.
================================================================================
*/

USE DATABASE MANUFACTURING_ANALYTICS;
USE SCHEMA RAW;
USE WAREHOUSE ANALYTICS_WH;

-- ============================================================================
-- STEP 1: Verify File is Staged
-- ============================================================================
-- List files in the stage to confirm upload was successful

LIST @RAW_DATA_STAGE;

-- ============================================================================
-- STEP 2: Preview Staged Data (Optional)
-- ============================================================================
-- Preview the file contents before loading to verify format

SELECT $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
FROM @RAW_DATA_STAGE/ai4i2020.csv
LIMIT 5;

-- ============================================================================
-- STEP 3: Load Data into Raw Table
-- ============================================================================
-- COPY INTO is the recommended method for bulk data loading.
-- ON_ERROR = 'ABORT_STATEMENT' ensures all-or-nothing loading.

COPY INTO MACHINE_SENSOR_DATA (
    type,
    air_temperature,
    process_temperature,
    rotational_speed,
    torque,
    tool_wear,
    machine_failure,
    twf,
    hdf,
    pwf,
    osf,
    rnf
)
FROM @RAW_DATA_STAGE/ai4i2020.csv
FILE_FORMAT = CSV_FORMAT
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;  -- Keep file in stage for audit/reload purposes

-- ============================================================================
-- STEP 4: Validate Load Results
-- ============================================================================

-- Check row count (expected: 10,000)
SELECT 
    'Row Count Check' AS validation,
    COUNT(*) AS actual_count,
    10000 AS expected_count,
    CASE WHEN COUNT(*) = 10000 THEN 'PASS' ELSE 'FAIL' END AS status
FROM MACHINE_SENSOR_DATA;

-- Check failure statistics (expected: 339 failures, 3.39% rate)
SELECT 
    'Failure Statistics' AS validation,
    COUNT(*) AS total_rows,
    SUM(machine_failure) AS failure_count,
    ROUND(SUM(machine_failure) * 100.0 / COUNT(*), 2) AS failure_rate_pct,
    CASE WHEN SUM(machine_failure) = 339 THEN 'PASS' ELSE 'FAIL' END AS status
FROM MACHINE_SENSOR_DATA;

-- Check machine type distribution (expected: L=50%, M=30%, H=20%)
SELECT 
    type AS machine_type,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentage
FROM MACHINE_SENSOR_DATA
GROUP BY type
ORDER BY type;

-- Check for NULL values (expected: 0)
SELECT 
    'NULL Value Check' AS validation,
    SUM(CASE WHEN type IS NULL THEN 1 ELSE 0 END) AS null_type,
    SUM(CASE WHEN air_temperature IS NULL THEN 1 ELSE 0 END) AS null_air_temp,
    SUM(CASE WHEN machine_failure IS NULL THEN 1 ELSE 0 END) AS null_failure,
    CASE 
        WHEN SUM(CASE WHEN type IS NULL OR air_temperature IS NULL OR machine_failure IS NULL THEN 1 ELSE 0 END) = 0 
        THEN 'PASS' ELSE 'FAIL' 
    END AS status
FROM MACHINE_SENSOR_DATA;

-- Preview loaded data
SELECT * FROM MACHINE_SENSOR_DATA LIMIT 10;

-- ============================================================================
-- End of Script
-- ============================================================================
