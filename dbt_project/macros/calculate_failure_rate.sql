{% macro calculate_failure_rate(failure_column, precision=2) %}
/*
    Macro: Calculate Failure Rate
    =============================
    Calculates failure rate as a percentage.
    
    Arguments:
      failure_column: Column containing 0/1 failure indicator
      precision: Decimal places for rounding (default: 2)
    
    Usage:
      select
          machine_type,
          {{ calculate_failure_rate('is_machine_failure') }} as failure_rate_pct
      from {{ ref('fct_failure_events') }}
      group by machine_type
*/
round(
    sum({{ failure_column }})::float / nullif(count(*), 0) * 100, 
    {{ precision }}
)
{% endmacro %}
