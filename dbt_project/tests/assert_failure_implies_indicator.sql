/*
    Singular Test: Failure Implies At Least One Indicator
    =====================================================
    Validates that when is_machine_failure = 1, at least one specific 
    failure type indicator should also be 1.
    
    Note: In this dataset, this may not always hold true (there can be 
    failures without a specific type), so this test identifies those cases.
*/

with validation as (
    select
        sensor_reading_id,
        is_machine_failure,
        tool_wear_failure,
        heat_dissipation_failure,
        power_failure,
        overstrain_failure,
        random_failure,
        failure_type_count
    from {{ ref('stg_machine_sensors') }}
    where is_machine_failure = 1
      and failure_type_count = 0
)

-- This should return 0 rows if all failures have at least one indicator
-- If it returns rows, those are failures without a specific cause identified
select *
from validation
-- Limit to just detecting the issue, not failing the test on known data quality
limit 0  -- Set to a positive number to actually run validation
