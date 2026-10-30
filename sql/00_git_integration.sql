/*
================================================================================
Manufacturing Analytics Platform - Snowflake Git Integration Setup
================================================================================
Purpose: Connect Snowflake directly to GitHub for version-controlled SQL execution.
         This enables running scripts directly from the repository.

Author: Anton Timokhin
Created: 2026-10-28

Prerequisites:
    - GitHub Personal Access Token with 'repo' scope
    - ACCOUNTADMIN role in Snowflake

Benefits:
    - Version-controlled SQL execution
    - Automatic sync with GitHub repository
    - Audit trail of script changes
    - Professional CI/CD-ready workflow
================================================================================
*/

USE ROLE ACCOUNTADMIN;
USE DATABASE MANUFACTURING_ANALYTICS;

-- ============================================================================
-- STEP 1: CREATE SECRET FOR GITHUB AUTHENTICATION
-- ============================================================================
-- Stores GitHub credentials securely in Snowflake
-- Replace <your-github-token> with your Personal Access Token

CREATE OR REPLACE SECRET GITHUB_SECRET
    TYPE = PASSWORD
    USERNAME = 'antimoh'
    PASSWORD = '<your-github-token>'
    COMMENT = 'GitHub PAT for repository access';

-- ============================================================================
-- STEP 2: CREATE API INTEGRATION
-- ============================================================================
-- Allows Snowflake to communicate with GitHub APIs

CREATE OR REPLACE API INTEGRATION GITHUB_INTEGRATION
    API_PROVIDER = GIT_HTTPS_API
    API_ALLOWED_PREFIXES = ('https://github.com/antimoh/')
    ALLOWED_AUTHENTICATION_SECRETS = (GITHUB_SECRET)
    ENABLED = TRUE
    COMMENT = 'Integration for GitHub repository access';

-- ============================================================================
-- STEP 3: CREATE GIT REPOSITORY CONNECTION
-- ============================================================================
-- Links the specific repository to Snowflake

CREATE OR REPLACE GIT REPOSITORY MANUFACTURING_REPO
    API_INTEGRATION = GITHUB_INTEGRATION
    GIT_CREDENTIALS = GITHUB_SECRET
    ORIGIN = 'https://github.com/antimoh/manufacturing-analytics-platform.git'
    COMMENT = 'Manufacturing Analytics Platform repository';

-- ============================================================================
-- STEP 4: FETCH LATEST FROM GITHUB
-- ============================================================================
-- Syncs the repository contents to Snowflake

ALTER GIT REPOSITORY MANUFACTURING_REPO FETCH;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- List available branches
SHOW GIT BRANCHES IN MANUFACTURING_REPO;

-- List SQL files in the repository
LS @MANUFACTURING_REPO/branches/main/sql/;

-- ============================================================================
-- USAGE: EXECUTE SCRIPTS FROM GITHUB
-- ============================================================================
-- Run SQL scripts directly from the repository:

-- USE WAREHOUSE ANALYTICS_WH;
-- EXECUTE IMMEDIATE FROM @MANUFACTURING_REPO/branches/main/sql/01_setup_database.sql;
-- EXECUTE IMMEDIATE FROM @MANUFACTURING_REPO/branches/main/sql/02_create_raw_objects.sql;
-- EXECUTE IMMEDIATE FROM @MANUFACTURING_REPO/branches/main/sql/03_load_raw_data.sql;
-- EXECUTE IMMEDIATE FROM @MANUFACTURING_REPO/branches/main/sql/04_validate_raw_data.sql;

-- ============================================================================
-- MAINTENANCE: SYNC WITH GITHUB
-- ============================================================================
-- Run this to pull the latest changes from GitHub:

-- ALTER GIT REPOSITORY MANUFACTURING_REPO FETCH;

-- ============================================================================
-- End of Script
-- ============================================================================
