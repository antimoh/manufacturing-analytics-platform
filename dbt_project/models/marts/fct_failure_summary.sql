{{
    config(
        materialized='table',
        tags=['marts', 'facts', 'summary']
    )
}}

/*
    Fact: Failure Summary
    =====================
    Aggregated failure statistics by machine type and failure type.
    Designed for dashboard KPIs and high-level failure analysis.
*/

with failure_events as (
    select * from {{ ref('fct_failure_events') }}
),

-- Failure type pivot
failure_by_type as (
    select
        machine_type,
        machine_type_description,
        primary_failure_type,
        count(*) as event_count,
        avg(risk_score) as avg_risk_score,
        avg(temperature_differential_k) as avg_temp_differential,
        avg(power_watts) as avg_power,
        avg(torque_nm) as avg_torque,
        avg(tool_wear_minutes) as avg_tool_wear
    from failure_events
    where is_machine_failure = 1
    group by machine_type, machine_type_description, primary_failure_type
),

-- Operating condition correlation
condition_analysis as (
    select
        machine_type,
        primary_failure_type,
        
        -- Temperature condition distribution
        sum(case when temperature_condition = 'Normal' then 1 else 0 end) as normal_temp_count,
        sum(case when temperature_condition = 'Elevated' then 1 else 0 end) as elevated_temp_count,
        sum(case when temperature_condition = 'Critical' then 1 else 0 end) as critical_temp_count,
        
        -- Tool wear condition distribution
        sum(case when tool_wear_condition = 'Low' then 1 else 0 end) as low_wear_count,
        sum(case when tool_wear_condition = 'Moderate' then 1 else 0 end) as moderate_wear_count,
        sum(case when tool_wear_condition = 'High' then 1 else 0 end) as high_wear_count,
        sum(case when tool_wear_condition = 'Critical' then 1 else 0 end) as critical_wear_count,
        
        -- Contributing conditions presence
        sum(case when hdf_conditions_present then 1 else 0 end) as hdf_conditions_count,
        sum(case when pwf_conditions_present then 1 else 0 end) as pwf_conditions_count,
        sum(case when twf_conditions_present then 1 else 0 end) as twf_conditions_count,
        sum(case when osf_conditions_present then 1 else 0 end) as osf_conditions_count
        
    from failure_events
    where is_machine_failure = 1
    group by machine_type, primary_failure_type
)

select
    {{ dbt_utils.generate_surrogate_key(['ft.machine_type', 'ft.primary_failure_type']) }} as summary_key,
    ft.machine_type,
    ft.machine_type_description,
    ft.primary_failure_type,
    ft.event_count,
    round(ft.avg_risk_score, 2) as avg_risk_score,
    round(ft.avg_temp_differential, 2) as avg_temp_differential_k,
    round(ft.avg_power, 0) as avg_power_watts,
    round(ft.avg_torque, 2) as avg_torque_nm,
    round(ft.avg_tool_wear, 0) as avg_tool_wear_minutes,
    
    -- Condition distributions
    ca.normal_temp_count,
    ca.elevated_temp_count,
    ca.critical_temp_count,
    ca.low_wear_count,
    ca.moderate_wear_count,
    ca.high_wear_count,
    ca.critical_wear_count,
    
    -- Contributing conditions
    ca.hdf_conditions_count,
    ca.pwf_conditions_count,
    ca.twf_conditions_count,
    ca.osf_conditions_count,
    
    current_timestamp() as dbt_updated_at
    
from failure_by_type ft
left join condition_analysis ca 
    on ft.machine_type = ca.machine_type 
    and ft.primary_failure_type = ca.primary_failure_type
