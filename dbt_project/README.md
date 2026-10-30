# Manufacturing Analytics - dbt Project

This dbt project transforms raw machine sensor data into analytics-ready models for predictive maintenance insights.

## Project Overview

### Data Flow

```
RAW.MACHINE_SENSOR_DATA
    │
    ▼
┌───────────────────────────────────────┐
│  STAGING (views)                      │
│  └── stg_machine_sensors              │
│      • Clean & standardize            │
│      • Add surrogate keys             │
│      • Calculate derived metrics      │
└───────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────┐
│  INTERMEDIATE (views)                 │
│  ├── int_machine_operating_conditions │
│  │   • Categorize conditions          │
│  │   • Calculate risk scores          │
│  └── int_failure_analysis             │
│      • Identify failure types         │
│      • Detect contributing factors    │
└───────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────┐
│  MARTS (tables)                       │
│  ├── dim_machine_types                │
│  │   • Machine type reference         │
│  ├── fct_failure_events               │
│  │   • All readings with analysis     │
│  ├── fct_failure_summary              │
│  │   • Aggregated failure stats       │
│  ├── fct_machine_performance          │
│  │   • Performance by type/risk       │
│  └── fct_predictive_indicators        │
│      • Maintenance priority flags     │
│      • Risk predictions               │
└───────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.9+
- Snowflake account with database `MANUFACTURING_ANALYTICS`
- RSA key pair configured (`~/.snowflake/rsa_key.p8`)

### Installation

1. Install dbt-snowflake:
   ```bash
   pip install dbt-snowflake>=1.7.0
   ```

2. Install dbt packages:
   ```bash
   cd dbt_project
   dbt deps
   ```

3. Set environment variables:
   ```powershell
   $env:SNOWFLAKE_ACCOUNT = "FYIUUJV-XJ40878"
   $env:SNOWFLAKE_USER = "ANTIMOH@GMAIL.COM"
   $env:SNOWFLAKE_PRIVATE_KEY_PATH = "~/.snowflake/rsa_key.p8"
   ```

### Running dbt

```bash
# Test connection
dbt debug

# Run all models
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve

# Full build (run + test)
dbt build
```

### Run Specific Model Groups

```bash
# Staging only
dbt run --select staging

# Marts only
dbt run --select marts

# Specific model and its dependencies
dbt run --select +fct_predictive_indicators
```

## Model Documentation

### Staging Layer

| Model | Description |
|-------|-------------|
| `stg_machine_sensors` | Cleaned sensor data with derived metrics (temperature differential, power watts) |

### Intermediate Layer

| Model | Description |
|-------|-------------|
| `int_machine_operating_conditions` | Categorized operating conditions and composite risk scores |
| `int_failure_analysis` | Failure type identification and contributing factor detection |

### Marts Layer

| Model | Description | Grain |
|-------|-------------|-------|
| `dim_machine_types` | Machine type reference with aggregated stats | One row per machine type |
| `fct_failure_events` | Complete failure analysis for all readings | One row per reading |
| `fct_failure_summary` | Aggregated failure statistics | One row per machine type × failure type |
| `fct_machine_performance` | Performance metrics by type and risk | One row per machine type × risk level |
| `fct_predictive_indicators` | Predictive maintenance flags and priorities | One row per reading |

### Seeds

| Seed | Description |
|------|-------------|
| `failure_type_reference` | Failure type codes, descriptions, and prevention strategies |
| `machine_type_reference` | Machine type codes with operational thresholds |

## Custom Macros

| Macro | Description | Usage |
|-------|-------------|-------|
| `calculate_failure_rate` | Calculates failure rate percentage | `{{ calculate_failure_rate('is_machine_failure') }}` |
| `kelvin_to_celsius` | Converts Kelvin to Celsius | `{{ kelvin_to_celsius('temp_k') }}` |
| `categorize_risk` | Converts risk score to level | `{{ categorize_risk('risk_score') }}` |

## Custom Tests

| Test | Description |
|------|-------------|
| `value_in_range` | Validates numeric values within expected range |
| `positive_value` | Validates positive numeric values |

## Configuration Variables

Defined in `dbt_project.yml`:

```yaml
vars:
  high_temp_threshold: 310.0      # Kelvin
  critical_temp_threshold: 315.0  # Kelvin
  moderate_wear_threshold: 100    # minutes
  high_wear_threshold: 180        # minutes
  critical_wear_threshold: 220    # minutes
  high_power_threshold: 9000      # Watts
  high_torque_threshold: 50       # Nm
  critical_torque_threshold: 65   # Nm
```

## Key Analytics Questions Answered

1. **What is the overall machine failure rate?**
   - Query `dim_machine_types` for `failure_rate_pct`

2. **Which machine types have higher failure rates?**
   - Query `dim_machine_types` grouped by `machine_type`

3. **What are the most common failure modes?**
   - Query `fct_failure_summary` for `event_count` by `primary_failure_type`

4. **How do operating conditions correlate with failures?**
   - Query `fct_failure_summary` for condition distributions
   - Analyze `fct_machine_performance` by `risk_level`

5. **Which machines need immediate maintenance?**
   - Query `fct_predictive_indicators` where `maintenance_priority = 'IMMEDIATE'`

## Predictive Model Validation

The `fct_predictive_indicators` model includes validation columns:
- `true_positive`: Correctly predicted failures
- `false_positive`: Predicted failure that didn't occur
- `false_negative`: Actual failure that wasn't predicted

Calculate precision, recall, and F1 score using these columns.

## Project Structure

```
dbt_project/
├── dbt_project.yml          # Project configuration
├── profiles.yml             # Connection profiles (key-pair auth)
├── packages.yml             # External packages (dbt_utils)
├── models/
│   ├── staging/
│   │   ├── sources.yml      # Source definitions
│   │   ├── stg_machine_sensors.sql
│   │   └── _staging__models.yml
│   ├── intermediate/
│   │   ├── int_machine_operating_conditions.sql
│   │   ├── int_failure_analysis.sql
│   │   └── _intermediate__models.yml
│   └── marts/
│       ├── dim_machine_types.sql
│       ├── fct_failure_events.sql
│       ├── fct_failure_summary.sql
│       ├── fct_machine_performance.sql
│       ├── fct_predictive_indicators.sql
│       └── _marts__models.yml
├── macros/
│   ├── calculate_failure_rate.sql
│   ├── kelvin_to_celsius.sql
│   ├── categorize_risk.sql
│   ├── test_value_in_range.sql
│   └── test_positive_value.sql
├── tests/
│   ├── assert_failure_counts_match.sql
│   ├── assert_temperature_differential_valid.sql
│   └── assert_predictive_model_has_coverage.sql
├── seeds/
│   ├── failure_type_reference.csv
│   ├── machine_type_reference.csv
│   └── _seeds__models.yml
└── README.md
```

## Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt-snowflake Setup](https://docs.getdbt.com/reference/warehouse-setups/snowflake-setup)
- [UCI AI4I 2020 Dataset](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)
