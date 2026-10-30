{{
    config(
        materialized='table',
        tags=['marts', 'facts', 'failures']
    )
}}

/*
    Fact: Failure Events
    ====================
    Core fact table containing all machine sensor readings with failure indicators.
    This table is the foundation for failure analysis and predictive maintenance dashboards.
*/

with failure_analysis as (
    select * from {{ ref('int_failure_analysis') }}
),

dim_machine as (
    select machine_type_key, machine_type
    from {{ ref('dim_machine_types') }}
),

final as (
    select
        -- Keys
        fa.sensor_reading_id,
        dm.machine_type_key,
        
        -- Machine attributes
        fa.machine_type,
        fa.machine_type_description,
        
        -- Temperature metrics
        fa.air_temperature_k,
        fa.process_temperature_k,
        fa.temperature_differential_k,
        fa.temperature_condition,
        
        -- Operational metrics
        fa.rotational_speed_rpm,
        fa.torque_nm,
        fa.tool_wear_minutes,
        fa.power_watts,
        
        -- Condition classifications
        fa.tool_wear_condition,
        fa.power_condition,
        fa.torque_condition,
        fa.speed_condition,
        
        -- Overstrain metrics
        fa.overstrain_factor,
        fa.overstrain_threshold,
        
        -- Risk assessment
        fa.risk_score,
        fa.risk_level,
        
        -- Failure indicators
        fa.is_machine_failure,
        fa.tool_wear_failure,
        fa.heat_dissipation_failure,
        fa.power_failure,
        fa.overstrain_failure,
        fa.random_failure,
        fa.failure_type_count,
        
        -- Failure classification
        fa.primary_failure_type,
        fa.failure_complexity,
        
        -- Contributing conditions
        fa.hdf_conditions_present,
        fa.pwf_conditions_present,
        fa.twf_conditions_present,
        fa.osf_conditions_present,
        
        -- Metadata
        fa.loaded_at,
        current_timestamp() as dbt_updated_at
        
    from failure_analysis fa
    left join dim_machine dm on fa.machine_type = dm.machine_type
)

select * from final
