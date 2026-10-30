{{
    config(
        materialized='view',
        tags=['intermediate', 'failure_analysis']
    )
}}

/*
    Intermediate Model: Failure Analysis Details
    ============================================
    Enriches failure data with detailed failure categorization and contributing factors.
    Focuses on records with failures for deeper analysis.
*/

with operating_conditions as (
    select * from {{ ref('int_machine_operating_conditions') }}
),

failure_details as (
    select
        sensor_reading_id,
        machine_type,
        machine_type_description,
        
        -- Temperature metrics
        air_temperature_k,
        process_temperature_k,
        temperature_differential_k,
        temperature_condition,
        
        -- Operational metrics
        rotational_speed_rpm,
        torque_nm,
        tool_wear_minutes,
        power_watts,
        
        -- Condition classifications
        tool_wear_condition,
        power_condition,
        torque_condition,
        speed_condition,
        
        -- Overstrain metrics
        overstrain_factor,
        overstrain_threshold,
        
        -- Risk indicators
        risk_score,
        risk_level,
        
        -- Failure indicators
        is_machine_failure,
        tool_wear_failure,
        heat_dissipation_failure,
        power_failure,
        overstrain_failure,
        random_failure,
        failure_type_count,
        
        -- Primary failure type identification
        case
            when tool_wear_failure = 1 then 'Tool Wear Failure'
            when heat_dissipation_failure = 1 then 'Heat Dissipation Failure'
            when power_failure = 1 then 'Power Failure'
            when overstrain_failure = 1 then 'Overstrain Failure'
            when random_failure = 1 then 'Random Failure'
            when is_machine_failure = 1 then 'Unknown Failure'
            else 'No Failure'
        end as primary_failure_type,
        
        -- Failure type combination (for multi-failure analysis)
        case
            when failure_type_count = 0 then 'No Failure'
            when failure_type_count = 1 then 'Single Failure'
            else 'Multiple Failures'
        end as failure_complexity,
        
        -- Contributing factors analysis
        case when temperature_differential_k < 8.6 and rotational_speed_rpm < 1380 
             then true else false end as hdf_conditions_present,
        case when power_watts < 3500 or power_watts > 9000 
             then true else false end as pwf_conditions_present,
        case when tool_wear_minutes between 200 and 240 
             then true else false end as twf_conditions_present,
        case when overstrain_factor > overstrain_threshold 
             then true else false end as osf_conditions_present,
        
        -- Metadata
        loaded_at
        
    from operating_conditions
)

select * from failure_details
