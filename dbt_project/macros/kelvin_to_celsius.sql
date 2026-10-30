{% macro kelvin_to_celsius(kelvin_column, precision=2) %}
/*
    Macro: Kelvin to Celsius
    ========================
    Converts temperature from Kelvin to Celsius.
    
    Arguments:
      kelvin_column: Column containing temperature in Kelvin
      precision: Decimal places for rounding (default: 2)
    
    Usage:
      select
          {{ kelvin_to_celsius('air_temperature_k') }} as air_temperature_c
      from my_model
*/
round({{ kelvin_column }} - 273.15, {{ precision }})
{% endmacro %}
