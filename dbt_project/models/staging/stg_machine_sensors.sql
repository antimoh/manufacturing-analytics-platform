{{
    config(
        materialized='view',
        tags=['staging', 'machine_data']
    )
}}

/*
    Staging Model: Machine Sensor Data
    ===================================
    Cleans and standardizes raw machine sensor data for downstream transformations.
    
    Transformations applied:
    - Renames columns to snake_case with descriptive names
    - Adds surrogate key for unique identification
    - Converts binary indicators to boolean-friendly naming
    - Preserves all original data for audit purposes
*/

with source as (
    select * from {{ source('raw', 'machine_sensor_data') }}
),

renamed as (
    select
        -- Surrogate key for unique identification
        {{ dbt_utils.generate_surrogate_key(['_loaded_at', 'type', 'air_temperature', 
            'process_temperature', 'rotational_speed', 'torque', 'tool_wear']) }} as sensor_reading_id,
        
        -- Machine classification
        type as machine_type,
        case type
            when 'L' then 'Low Quality'
            when 'M' then 'Medium Quality'
            when 'H' then 'High Quality'
        end as machine_type_description,
        
        -- Temperature readings (Kelvin)
        air_temperature as air_temperature_k,
        process_temperature as process_temperature_k,
        
        -- Derived temperature metrics
        process_temperature - air_temperature as temperature_differential_k,
        
        -- Operational parameters
        rotational_speed as rotational_speed_rpm,
        torque as torque_nm,
        tool_wear as tool_wear_minutes,
        
        -- Calculated power (Watts) = Torque (Nm) × Angular velocity (rad/s)
        -- Angular velocity = RPM × 2π / 60
        torque * rotational_speed * 2 * 3.14159265359 / 60 as power_watts,
        
        -- Overall failure indicator
        machine_failure as is_machine_failure,
        
        -- Specific failure type indicators (keeping original 0/1 for aggregations)
        twf as tool_wear_failure,
        hdf as heat_dissipation_failure,
        pwf as power_failure,
        osf as overstrain_failure,
        rnf as random_failure,
        
        -- Count of failure types for this reading
        twf + hdf + pwf + osf + rnf as failure_type_count,
        
        -- Metadata
        _loaded_at as loaded_at
        
    from source
)

select * from renamed
