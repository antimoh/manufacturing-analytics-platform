{{
    config(
        materialized='table',
        tags=['marts', 'facts', 'performance']
    )
}}

/*
    Fact: Machine Performance Metrics
    =================================
    Aggregated machine performance statistics by machine type and operating conditions.
    Designed for operational monitoring and performance benchmarking.
*/

with operating_conditions as (
    select * from {{ ref('int_machine_operating_conditions') }}
),

-- Performance by machine type and risk level
performance_summary as (
    select
        machine_type,
        machine_type_description,
        risk_level,
        
        -- Record counts
        count(*) as reading_count,
        sum(is_machine_failure) as failure_count,
        round(sum(is_machine_failure)::float / count(*) * 100, 2) as failure_rate_pct,
        
        -- Temperature statistics
        round(avg(air_temperature_k), 2) as avg_air_temp_k,
        round(min(air_temperature_k), 2) as min_air_temp_k,
        round(max(air_temperature_k), 2) as max_air_temp_k,
        round(avg(process_temperature_k), 2) as avg_process_temp_k,
        round(min(process_temperature_k), 2) as min_process_temp_k,
        round(max(process_temperature_k), 2) as max_process_temp_k,
        round(avg(temperature_differential_k), 2) as avg_temp_differential_k,
        
        -- Speed statistics
        round(avg(rotational_speed_rpm), 0) as avg_speed_rpm,
        round(min(rotational_speed_rpm), 0) as min_speed_rpm,
        round(max(rotational_speed_rpm), 0) as max_speed_rpm,
        
        -- Torque statistics
        round(avg(torque_nm), 2) as avg_torque_nm,
        round(min(torque_nm), 2) as min_torque_nm,
        round(max(torque_nm), 2) as max_torque_nm,
        
        -- Tool wear statistics
        round(avg(tool_wear_minutes), 0) as avg_tool_wear_min,
        round(min(tool_wear_minutes), 0) as min_tool_wear_min,
        round(max(tool_wear_minutes), 0) as max_tool_wear_min,
        
        -- Power statistics
        round(avg(power_watts), 0) as avg_power_watts,
        round(min(power_watts), 0) as min_power_watts,
        round(max(power_watts), 0) as max_power_watts,
        
        -- Overstrain metrics
        round(avg(overstrain_factor), 0) as avg_overstrain_factor,
        max(overstrain_threshold) as overstrain_threshold,
        
        -- Risk score average
        round(avg(risk_score), 2) as avg_risk_score
        
    from operating_conditions
    group by machine_type, machine_type_description, risk_level
)

select
    {{ dbt_utils.generate_surrogate_key(['machine_type', 'risk_level']) }} as performance_key,
    *,
    current_timestamp() as dbt_updated_at
from performance_summary
