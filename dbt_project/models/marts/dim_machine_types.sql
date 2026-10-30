{{
    config(
        materialized='table',
        tags=['marts', 'dimensions']
    )
}}

/*
    Dimension: Machine Types
    ========================
    Reference dimension for machine quality variants with aggregated performance statistics.
*/

with failure_data as (
    select * from {{ ref('int_failure_analysis') }}
),

machine_type_stats as (
    select
        machine_type,
        machine_type_description,
        
        -- Record counts
        count(*) as total_readings,
        sum(is_machine_failure) as total_failures,
        
        -- Failure rate
        round(sum(is_machine_failure)::float / count(*) * 100, 2) as failure_rate_pct,
        
        -- Failure type breakdowns
        sum(tool_wear_failure) as tool_wear_failures,
        sum(heat_dissipation_failure) as heat_dissipation_failures,
        sum(power_failure) as power_failures,
        sum(overstrain_failure) as overstrain_failures,
        sum(random_failure) as random_failures,
        
        -- Operational statistics
        round(avg(air_temperature_k), 2) as avg_air_temperature_k,
        round(avg(process_temperature_k), 2) as avg_process_temperature_k,
        round(avg(temperature_differential_k), 2) as avg_temperature_differential_k,
        round(avg(rotational_speed_rpm), 0) as avg_rotational_speed_rpm,
        round(avg(torque_nm), 2) as avg_torque_nm,
        round(avg(tool_wear_minutes), 0) as avg_tool_wear_minutes,
        round(avg(power_watts), 0) as avg_power_watts,
        
        -- Range statistics for tool wear
        min(tool_wear_minutes) as min_tool_wear_minutes,
        max(tool_wear_minutes) as max_tool_wear_minutes,
        
        -- Overstrain thresholds per type
        max(overstrain_threshold) as overstrain_threshold
        
    from failure_data
    group by machine_type, machine_type_description
)

select
    -- Surrogate key
    {{ dbt_utils.generate_surrogate_key(['machine_type']) }} as machine_type_key,
    *
from machine_type_stats
