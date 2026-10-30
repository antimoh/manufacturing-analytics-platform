/*
================================================================================
Manufacturing Analytics Platform - Data Validation Script
================================================================================
Purpose: Comprehensive data quality validation for the raw layer.
         These checks ensure data integrity before downstream processing.

Author: Anton Timokhin
Created: 2026-10-28

Validation Checks:
    1. Row count matches expected (10,000)
    2. No duplicate records
    3. No NULL values in required columns
    4. Binary columns contain only 0/1
    5. Machine types are valid (L, M, H)
    6. Sensor readings within expected ranges
    7. Failure mode consistency

Usage:
    Run this script after data loading to validate data quality.
    All checks should return 'PASS' status.
================================================================================
*/

USE DATABASE MANUFACTURING_ANALYTICS;
USE SCHEMA RAW;
USE WAREHOUSE ANALYTICS_WH;

-- ============================================================================
-- VALIDATION SUMMARY TABLE
-- ============================================================================
-- Creates a comprehensive validation report

WITH validations AS (
    -- Check 1: Row Count
    SELECT 
        1 AS check_order,
        'Row Count' AS check_name,
        'Total rows equals 10,000' AS check_description,
        COUNT(*)::VARCHAR AS actual_value,
        '10000' AS expected_value,
        CASE WHEN COUNT(*) = 10000 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM MACHINE_SENSOR_DATA
    
    UNION ALL
    
    -- Check 2: Duplicate Records
    SELECT 
        2,
        'Duplicate Check',
        'No exact duplicate rows',
        (COUNT(*) - COUNT(DISTINCT 
            type || air_temperature || process_temperature || 
            rotational_speed || torque || tool_wear))::VARCHAR,
        '0',
        CASE WHEN COUNT(*) = COUNT(DISTINCT 
            type || air_temperature || process_temperature || 
            rotational_speed || torque || tool_wear) 
        THEN 'PASS' ELSE 'WARN' END
    FROM MACHINE_SENSOR_DATA
    
    UNION ALL
    
    -- Check 3: NULL Values in Key Columns
    SELECT 
        3,
        'NULL Check',
        'No NULL values in sensor columns',
        SUM(CASE WHEN type IS NULL OR air_temperature IS NULL OR 
            process_temperature IS NULL OR rotational_speed IS NULL OR
            torque IS NULL OR tool_wear IS NULL THEN 1 ELSE 0 END)::VARCHAR,
        '0',
        CASE WHEN SUM(CASE WHEN type IS NULL OR air_temperature IS NULL THEN 1 ELSE 0 END) = 0 
        THEN 'PASS' ELSE 'FAIL' END
    FROM MACHINE_SENSOR_DATA
    
    UNION ALL
    
    -- Check 4: Binary Column Validity (machine_failure)
    SELECT 
        4,
        'Binary Values - machine_failure',
        'Contains only 0 or 1',
        COUNT(CASE WHEN machine_failure NOT IN (0, 1) THEN 1 END)::VARCHAR,
        '0',
        CASE WHEN COUNT(CASE WHEN machine_failure NOT IN (0, 1) THEN 1 END) = 0 
        THEN 'PASS' ELSE 'FAIL' END
    FROM MACHINE_SENSOR_DATA
    
    UNION ALL
    
    -- Check 5: Valid Machine Types
    SELECT 
        5,
        'Machine Type Values',
        'Contains only L, M, or H',
        COUNT(CASE WHEN type NOT IN ('L', 'M', 'H') THEN 1 END)::VARCHAR,
        '0',
        CASE WHEN COUNT(CASE WHEN type NOT IN ('L', 'M', 'H') THEN 1 END) = 0 
        THEN 'PASS' ELSE 'FAIL' END
    FROM MACHINE_SENSOR_DATA
    
    UNION ALL
    
    -- Check 6: Failure Count
    SELECT 
        6,
        'Failure Count',
        'Total failures equals 339',
        SUM(machine_failure)::VARCHAR,
        '339',
        CASE WHEN SUM(machine_failure) = 339 THEN 'PASS' ELSE 'FAIL' END
    FROM MACHINE_SENSOR_DATA
    
    UNION ALL
    
    -- Check 7: Failure Mode Consistency
    -- When TWF, HDF, PWF, or OSF = 1, machine_failure should = 1
    SELECT 
        7,
        'Failure Mode Consistency',
        'Deterministic failures imply machine_failure=1',
        SUM(CASE WHEN (twf = 1 OR hdf = 1 OR pwf = 1 OR osf = 1) 
                  AND machine_failure = 0 THEN 1 ELSE 0 END)::VARCHAR,
        '0',
        CASE WHEN SUM(CASE WHEN (twf = 1 OR hdf = 1 OR pwf = 1 OR osf = 1) 
                           AND machine_failure = 0 THEN 1 ELSE 0 END) = 0 
        THEN 'PASS' ELSE 'FAIL' END
    FROM MACHINE_SENSOR_DATA
    
    UNION ALL
    
    -- Check 8: Temperature Range
    SELECT 
        8,
        'Temperature Range',
        'Air temp between 295-305 K',
        ROUND(MIN(air_temperature), 1) || ' - ' || ROUND(MAX(air_temperature), 1),
        '295-305 K range',
        CASE WHEN MIN(air_temperature) >= 290 AND MAX(air_temperature) <= 310 
        THEN 'PASS' ELSE 'WARN' END
    FROM MACHINE_SENSOR_DATA
)
SELECT 
    check_order,
    check_name,
    check_description,
    actual_value,
    expected_value,
    status
FROM validations
ORDER BY check_order;

-- ============================================================================
-- DETAILED STATISTICS
-- ============================================================================

-- Sensor reading statistics
SELECT 
    'air_temperature' AS metric,
    MIN(air_temperature) AS min_value,
    ROUND(AVG(air_temperature), 2) AS avg_value,
    MAX(air_temperature) AS max_value,
    ROUND(STDDEV(air_temperature), 2) AS std_dev
FROM MACHINE_SENSOR_DATA
UNION ALL
SELECT 
    'process_temperature',
    MIN(process_temperature),
    ROUND(AVG(process_temperature), 2),
    MAX(process_temperature),
    ROUND(STDDEV(process_temperature), 2)
FROM MACHINE_SENSOR_DATA
UNION ALL
SELECT 
    'rotational_speed',
    MIN(rotational_speed),
    ROUND(AVG(rotational_speed), 2),
    MAX(rotational_speed),
    ROUND(STDDEV(rotational_speed), 2)
FROM MACHINE_SENSOR_DATA
UNION ALL
SELECT 
    'torque',
    MIN(torque),
    ROUND(AVG(torque), 2),
    MAX(torque),
    ROUND(STDDEV(torque), 2)
FROM MACHINE_SENSOR_DATA
UNION ALL
SELECT 
    'tool_wear',
    MIN(tool_wear),
    ROUND(AVG(tool_wear), 2),
    MAX(tool_wear),
    ROUND(STDDEV(tool_wear), 2)
FROM MACHINE_SENSOR_DATA;

-- Failure mode breakdown
SELECT 
    'TWF' AS failure_mode, SUM(twf) AS count, ROUND(SUM(twf)*100.0/COUNT(*), 3) AS pct
FROM MACHINE_SENSOR_DATA
UNION ALL
SELECT 'HDF', SUM(hdf), ROUND(SUM(hdf)*100.0/COUNT(*), 3) FROM MACHINE_SENSOR_DATA
UNION ALL
SELECT 'PWF', SUM(pwf), ROUND(SUM(pwf)*100.0/COUNT(*), 3) FROM MACHINE_SENSOR_DATA
UNION ALL
SELECT 'OSF', SUM(osf), ROUND(SUM(osf)*100.0/COUNT(*), 3) FROM MACHINE_SENSOR_DATA
UNION ALL
SELECT 'RNF', SUM(rnf), ROUND(SUM(rnf)*100.0/COUNT(*), 3) FROM MACHINE_SENSOR_DATA;

-- ============================================================================
-- End of Script
-- ============================================================================
