{{
    config(
        materialized='view',
        tags=['intermediate', 'operating_conditions']
    )
}}

/*
    Intermediate Model: Machine Operating Conditions
    =================================================
    Enriches sensor data with categorized operating conditions and risk indicators.
    This model applies business logic to classify machine states for analytics.
*/

with staged as (
    select * from {{ ref('stg_machine_sensors') }}
),

with_conditions as (
    select
        *,
        
        -- Temperature condition categories
        case
            when process_temperature_k >= {{ var('critical_temp_threshold') }} then 'Critical'
            when process_temperature_k >= {{ var('high_temp_threshold') }} then 'Elevated'
            else 'Normal'
        end as temperature_condition,
        
        -- Tool wear condition categories
        case
            when tool_wear_minutes >= {{ var('critical_wear_threshold') }} then 'Critical'
            when tool_wear_minutes >= {{ var('high_wear_threshold') }} then 'High'
            when tool_wear_minutes >= {{ var('moderate_wear_threshold') }} then 'Moderate'
            else 'Low'
        end as tool_wear_condition,
        
        -- Power condition categories
        case
            when power_watts >= {{ var('high_power_threshold') }} then 'High'
            when power_watts < 3500 then 'Low'
            else 'Normal'
        end as power_condition,
        
        -- Torque condition categories
        case
            when torque_nm >= {{ var('critical_torque_threshold') }} then 'Critical'
            when torque_nm >= {{ var('high_torque_threshold') }} then 'High'
            else 'Normal'
        end as torque_condition,
        
        -- Speed categories (based on dataset distribution)
        case
            when rotational_speed_rpm < 1400 then 'Low'
            when rotational_speed_rpm > 2500 then 'High'
            else 'Normal'
        end as speed_condition,
        
        -- Calculate overstrain factor (tool_wear × torque)
        tool_wear_minutes * torque_nm as overstrain_factor,
        
        -- Overstrain threshold per machine type
        case machine_type
            when 'L' then 11000
            when 'M' then 12000
            when 'H' then 13000
        end as overstrain_threshold
        
    from staged
),

with_risk_indicators as (
    select
        *,
        
        -- Risk score (0-5 based on condition flags)
        (case when temperature_condition in ('Critical', 'Elevated') then 1 else 0 end) +
        (case when tool_wear_condition in ('Critical', 'High') then 1 else 0 end) +
        (case when power_condition != 'Normal' then 1 else 0 end) +
        (case when torque_condition in ('Critical', 'High') then 1 else 0 end) +
        (case when overstrain_factor > overstrain_threshold * 0.9 then 1 else 0 end) as risk_score,
        
        -- Risk level categorization
        case
            when (case when temperature_condition in ('Critical', 'Elevated') then 1 else 0 end) +
                 (case when tool_wear_condition in ('Critical', 'High') then 1 else 0 end) +
                 (case when power_condition != 'Normal' then 1 else 0 end) +
                 (case when torque_condition in ('Critical', 'High') then 1 else 0 end) +
                 (case when overstrain_factor > overstrain_threshold * 0.9 then 1 else 0 end) >= 3 then 'High'
            when (case when temperature_condition in ('Critical', 'Elevated') then 1 else 0 end) +
                 (case when tool_wear_condition in ('Critical', 'High') then 1 else 0 end) +
                 (case when power_condition != 'Normal' then 1 else 0 end) +
                 (case when torque_condition in ('Critical', 'High') then 1 else 0 end) +
                 (case when overstrain_factor > overstrain_threshold * 0.9 then 1 else 0 end) >= 2 then 'Medium'
            when (case when temperature_condition in ('Critical', 'Elevated') then 1 else 0 end) +
                 (case when tool_wear_condition in ('Critical', 'High') then 1 else 0 end) +
                 (case when power_condition != 'Normal' then 1 else 0 end) +
                 (case when torque_condition in ('Critical', 'High') then 1 else 0 end) +
                 (case when overstrain_factor > overstrain_threshold * 0.9 then 1 else 0 end) >= 1 then 'Low'
            else 'Minimal'
        end as risk_level
        
    from with_conditions
)

select * from with_risk_indicators
