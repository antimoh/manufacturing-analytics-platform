{% test positive_value(model, column_name) %}
/*
    Custom Test: Positive Value
    ==========================
    Validates that a numeric column contains only positive values (> 0).
    
    Usage in schema.yml:
      tests:
        - positive_value
*/

select
    {{ column_name }} as invalid_value,
    count(*) as occurrences
from {{ model }}
where {{ column_name }} <= 0
group by {{ column_name }}
having count(*) > 0

{% endtest %}
