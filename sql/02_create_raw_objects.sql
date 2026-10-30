/*
================================================================================
Manufacturing Analytics Platform - Raw Layer Objects
================================================================================
Purpose: Create file format, stage, and raw table for data loading.
         Establishes a reproducible data ingestion pipeline.

Author: Anton Timokhin
Created: 2026-10-28

Data Source:
    UCI AI4I 2020 Predictive Maintenance Dataset
    URL: https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset
    DOI: https://doi.org/10.24432/C5HS5C
    License: CC BY 4.0

Usage:
    Run this script after 01_setup_database.sql to create the raw layer
    infrastructure needed for data loading.
================================================================================
*/

USE DATABASE MANUFACTURING_ANALYTICS;
USE SCHEMA RAW;
USE WAREHOUSE ANALYTICS_WH;

-- ============================================================================
-- STEP 1: Create File Format
-- ============================================================================
-- Defines how to parse the CSV file consistently and repeatably.
-- This format can be reused for any similarly structured CSV files.

CREATE FILE FORMAT IF NOT EXISTS CSV_FORMAT
    TYPE = 'CSV'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1                    -- First row contains column names
    NULL_IF = ('', 'NULL', 'null')     -- Treat empty strings as NULL
    TRIM_SPACE = TRUE                  -- Remove leading/trailing whitespace
    ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE
    COMMENT = 'Standard CSV format with header row for data ingestion';

-- ============================================================================
-- STEP 2: Create Internal Stage
-- ============================================================================
-- Internal stage for uploading files from local machine.
-- Files uploaded here are stored in Snowflake-managed cloud storage.

CREATE STAGE IF NOT EXISTS RAW_DATA_STAGE
    FILE_FORMAT = CSV_FORMAT
    COMMENT = 'Internal stage for raw data file uploads';

-- ============================================================================
-- STEP 3: Create Raw Table
-- ============================================================================
-- Raw table structure matches the UCI dataset exactly.
-- Column names are standardized to snake_case for consistency.
--
-- Original Columns -> Standardized Names:
--   Type                  -> type (machine quality variant: L, M, H)
--   Air temperature [K]   -> air_temperature (Kelvin)
--   Process temperature   -> process_temperature (Kelvin)
--   Rotational speed      -> rotational_speed (RPM)
--   Torque [Nm]          -> torque (Newton-meters)
--   Tool wear [min]      -> tool_wear (minutes)
--   Machine failure      -> machine_failure (binary: 0/1)
--   TWF                  -> twf (Tool Wear Failure)
--   HDF                  -> hdf (Heat Dissipation Failure)
--   PWF                  -> pwf (Power Failure)
--   OSF                  -> osf (Overstrain Failure)
--   RNF                  -> rnf (Random Failure)

CREATE TABLE IF NOT EXISTS MACHINE_SENSOR_DATA (
    -- Machine identifier
    type                    VARCHAR(1)      COMMENT 'Machine type: L=Low, M=Medium, H=High quality variant',
    
    -- Sensor readings
    air_temperature         FLOAT           COMMENT 'Air temperature in Kelvin',
    process_temperature     FLOAT           COMMENT 'Process temperature in Kelvin',
    rotational_speed        INTEGER         COMMENT 'Rotational speed in RPM',
    torque                  FLOAT           COMMENT 'Torque in Newton-meters',
    tool_wear               INTEGER         COMMENT 'Tool wear in minutes',
    
    -- Failure indicators (binary: 0 = no failure, 1 = failure)
    machine_failure         INTEGER         COMMENT 'Overall machine failure indicator (0/1)',
    twf                     INTEGER         COMMENT 'Tool Wear Failure indicator (0/1)',
    hdf                     INTEGER         COMMENT 'Heat Dissipation Failure indicator (0/1)',
    pwf                     INTEGER         COMMENT 'Power Failure indicator (0/1)',
    osf                     INTEGER         COMMENT 'Overstrain Failure indicator (0/1)',
    rnf                     INTEGER         COMMENT 'Random Failure indicator (0/1)',
    
    -- Metadata columns for data lineage
    _loaded_at              TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP() 
                                            COMMENT 'Timestamp when record was loaded'
)
COMMENT = 'Raw machine sensor data from UCI AI4I 2020 Predictive Maintenance Dataset';

-- ============================================================================
-- STEP 4: Verify Objects Created
-- ============================================================================
SHOW FILE FORMATS IN SCHEMA RAW;
SHOW STAGES IN SCHEMA RAW;
DESCRIBE TABLE MACHINE_SENSOR_DATA;

-- ============================================================================
-- End of Script
-- ============================================================================
