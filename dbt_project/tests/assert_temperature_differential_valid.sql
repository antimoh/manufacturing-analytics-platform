/*
    Singular Test: Temperature Differential Valid
    =============================================
    Validates that process temperature is always higher than air temperature
    (temperature differential should always be positive).
    
    Based on dataset documentation: process temp = air temp + ~10K
*/

select
    sensor_reading_id,
    air_temperature_k,
    process_temperature_k,
    temperature_differential_k
from {{ ref('stg_machine_sensors') }}
where temperature_differential_k <= 0
