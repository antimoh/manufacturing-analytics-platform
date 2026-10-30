{% test value_in_range(model, column_name, min_value, max_value) %}
/*
    Custom Test: Value In Range
    ===========================
    Validates that a numeric column's values fall within an expected range.
    
    Arguments:
      min_value: Minimum allowed value (inclusive)
      max_value: Maximum allowed value (inclusive)
    
    Usage in schema.yml:
      tests:
        - value_in_range:
            min_value: 295
            max_value: 320
*/

select
    {{ column_name }} as out_of_range_value,
    count(*) as occurrences
from {{ model }}
where {{ column_name }} < {{ min_value }} 
   or {{ column_name }} > {{ max_value }}
group by {{ column_name }}
having count(*) > 0

{% endtest %}
