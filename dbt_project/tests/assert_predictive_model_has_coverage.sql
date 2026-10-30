/*
    Singular Test: Predictive Model Has Coverage
    ============================================
    Validates that the predictive indicators model captures a meaningful
    portion of actual failures (recall > 50%).
    
    This ensures the threshold-based rules are working reasonably well.
*/

with metrics as (
    select
        sum(is_machine_failure) as total_actual_failures,
        sum(true_positive) as captured_failures,
        sum(false_negative) as missed_failures
    from {{ ref('fct_predictive_indicators') }}
)

select 
    total_actual_failures,
    captured_failures,
    missed_failures,
    round(captured_failures::float / nullif(total_actual_failures, 0) * 100, 1) as recall_pct
from metrics
where captured_failures::float / nullif(total_actual_failures, 0) < 0.5
