/*
    Singular Test: Failure Counts Match
    ===================================
    Validates that the sum of individual failure types equals total failures
    when failure_type_count > 0.
    
    This ensures data integrity between the overall failure flag and
    the individual failure type indicators.
*/

with validation as (
    select
        sensor_reading_id,
        is_machine_failure,
        tool_wear_failure + heat_dissipation_failure + power_failure + 
            overstrain_failure + random_failure as calculated_failure_count,
        failure_type_count
    from {{ ref('stg_machine_sensors') }}
)

-- Find records where calculated count doesn't match stored count
select *
from validation
where calculated_failure_count != failure_type_count
