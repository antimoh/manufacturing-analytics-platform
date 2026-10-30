{% macro categorize_risk(risk_score_column) %}
/*
    Macro: Categorize Risk
    ======================
    Converts a numeric risk score (0-5) to a categorical risk level.
    
    Arguments:
      risk_score_column: Column containing numeric risk score
    
    Usage:
      select
          {{ categorize_risk('risk_score') }} as risk_level
      from my_model
*/
case
    when {{ risk_score_column }} >= 3 then 'High'
    when {{ risk_score_column }} >= 2 then 'Medium'
    when {{ risk_score_column }} >= 1 then 'Low'
    else 'Minimal'
end
{% endmacro %}
