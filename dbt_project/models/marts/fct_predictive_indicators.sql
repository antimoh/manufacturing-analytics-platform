{{
    config(
        materialized='table',
        tags=['marts', 'facts', 'predictive']
    )
}}

/*
    Fact: Predictive Maintenance Indicators
    =======================================
    Identifies high-risk machine readings for predictive maintenance.
    Uses threshold-based rules derived from failure mode analysis.
    
    Each reading is scored and flagged based on conditions known to 
    correlate with specific failure types.
*/

with operating_conditions as (
    select * from {{ ref('int_machine_operating_conditions') }}
),

predictive_flags as (
    select
        sensor_reading_id,
        machine_type,
        machine_type_description,
        
        -- Core metrics
        air_temperature_k,
        process_temperature_k,
        temperature_differential_k,
        rotational_speed_rpm,
        torque_nm,
        tool_wear_minutes,
        power_watts,
        overstrain_factor,
        overstrain_threshold,
        
        -- Existing conditions
        temperature_condition,
        tool_wear_condition,
        power_condition,
        torque_condition,
        speed_condition,
        risk_score,
        risk_level,
        
        -- Actual failure (for validation/training)
        is_machine_failure,
        
        -- HDF Risk: Low temp differential AND low speed
        case 
            when temperature_differential_k < 8.6 and rotational_speed_rpm < 1380 
            then 'HIGH'
            when temperature_differential_k < 9.0 and rotational_speed_rpm < 1500 
            then 'MEDIUM'
            else 'LOW'
        end as hdf_risk_indicator,
        
        -- PWF Risk: Power outside normal operating range
        case 
            when power_watts < 3500 or power_watts > 9000 then 'HIGH'
            when power_watts < 4000 or power_watts > 8500 then 'MEDIUM'
            else 'LOW'
        end as pwf_risk_indicator,
        
        -- TWF Risk: Tool approaching end of life
        case 
            when tool_wear_minutes >= 220 then 'CRITICAL'
            when tool_wear_minutes >= 200 then 'HIGH'
            when tool_wear_minutes >= 180 then 'MEDIUM'
            else 'LOW'
        end as twf_risk_indicator,
        
        -- OSF Risk: High overstrain factor
        case 
            when overstrain_factor > overstrain_threshold then 'CRITICAL'
            when overstrain_factor > overstrain_threshold * 0.95 then 'HIGH'
            when overstrain_factor > overstrain_threshold * 0.85 then 'MEDIUM'
            else 'LOW'
        end as osf_risk_indicator,
        
        -- Combined maintenance priority
        case
            when tool_wear_minutes >= 220 
                 or overstrain_factor > overstrain_threshold 
            then 'IMMEDIATE'
            when (temperature_differential_k < 8.6 and rotational_speed_rpm < 1380)
                 or power_watts < 3500 
                 or power_watts > 9000
                 or tool_wear_minutes >= 200
            then 'URGENT'
            when risk_score >= 3 then 'SCHEDULED'
            when risk_score >= 2 then 'MONITOR'
            else 'NORMAL'
        end as maintenance_priority,
        
        loaded_at
        
    from operating_conditions
),

with_validation as (
    select
        *,
        
        -- Predicted failure (any HIGH/CRITICAL indicator = predicted failure)
        case 
            when hdf_risk_indicator in ('HIGH')
                 or pwf_risk_indicator in ('HIGH')
                 or twf_risk_indicator in ('CRITICAL', 'HIGH')
                 or osf_risk_indicator in ('CRITICAL', 'HIGH')
            then 1 
            else 0 
        end as predicted_failure,
        
        -- True positive: predicted AND actual failure
        case 
            when is_machine_failure = 1 
                 and (hdf_risk_indicator in ('HIGH')
                      or pwf_risk_indicator in ('HIGH')
                      or twf_risk_indicator in ('CRITICAL', 'HIGH')
                      or osf_risk_indicator in ('CRITICAL', 'HIGH'))
            then 1 
            else 0 
        end as true_positive,
        
        -- False positive: predicted but no actual failure
        case 
            when is_machine_failure = 0 
                 and (hdf_risk_indicator in ('HIGH')
                      or pwf_risk_indicator in ('HIGH')
                      or twf_risk_indicator in ('CRITICAL', 'HIGH')
                      or osf_risk_indicator in ('CRITICAL', 'HIGH'))
            then 1 
            else 0 
        end as false_positive,
        
        -- False negative: actual failure but not predicted
        case 
            when is_machine_failure = 1 
                 and not (hdf_risk_indicator in ('HIGH')
                          or pwf_risk_indicator in ('HIGH')
                          or twf_risk_indicator in ('CRITICAL', 'HIGH')
                          or osf_risk_indicator in ('CRITICAL', 'HIGH'))
            then 1 
            else 0 
        end as false_negative,
        
        current_timestamp() as dbt_updated_at
        
    from predictive_flags
)

select * from with_validation
