/*
================================================================================
Manufacturing Analytics Platform - Database Setup
================================================================================
Purpose: Create the foundational database infrastructure for the project.
         This script is idempotent and can be run multiple times safely.

Author: Anton Timokhin
Created: 2026-10-28

Usage:
    Run this script in Snowsight or via SnowSQL to set up the database,
    schemas, and warehouse for the Manufacturing Analytics Platform.

Prerequisites:
    - Snowflake account with ACCOUNTADMIN or equivalent privileges
    - Sufficient credits for warehouse operations
================================================================================
*/

-- ============================================================================
-- STEP 1: Create Database
-- ============================================================================
-- The MANUFACTURING_ANALYTICS database serves as the central repository
-- for all manufacturing sensor data and analytical models.

CREATE DATABASE IF NOT EXISTS MANUFACTURING_ANALYTICS
    COMMENT = 'Manufacturing Analytics Platform - Portfolio Project';

USE DATABASE MANUFACTURING_ANALYTICS;

-- ============================================================================
-- STEP 2: Create Schemas (Data Layers)
-- ============================================================================
-- We follow a medallion-style architecture with three layers:
--   RAW       - Source data as loaded, no transformations
--   STAGING   - Cleaned, standardized, and validated data
--   ANALYTICS - Business-ready analytical models and metrics

CREATE SCHEMA IF NOT EXISTS RAW
    COMMENT = 'Raw source data - loaded as-is from external sources';

CREATE SCHEMA IF NOT EXISTS STAGING
    COMMENT = 'Staging layer - cleaned and standardized data';

CREATE SCHEMA IF NOT EXISTS ANALYTICS
    COMMENT = 'Analytics layer - business-ready models and metrics';

-- ============================================================================
-- STEP 3: Create Warehouse
-- ============================================================================
-- X-SMALL warehouse with aggressive auto-suspend for cost efficiency.
-- Auto-resume ensures seamless query execution when needed.

CREATE WAREHOUSE IF NOT EXISTS ANALYTICS_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60              -- Suspend after 60 seconds idle
    AUTO_RESUME = TRUE             -- Resume automatically on query
    INITIALLY_SUSPENDED = TRUE     -- Start suspended to save credits
    COMMENT = 'Analytics warehouse for Manufacturing Analytics Platform';

-- ============================================================================
-- STEP 4: Set Session Context
-- ============================================================================
USE WAREHOUSE ANALYTICS_WH;
USE DATABASE MANUFACTURING_ANALYTICS;
USE SCHEMA RAW;

-- ============================================================================
-- STEP 5: Verify Setup
-- ============================================================================
SELECT 
    CURRENT_WAREHOUSE() AS warehouse,
    CURRENT_DATABASE() AS database,
    CURRENT_SCHEMA() AS schema,
    CURRENT_ROLE() AS role;

SHOW SCHEMAS IN DATABASE MANUFACTURING_ANALYTICS;

-- ============================================================================
-- End of Script
-- ============================================================================
