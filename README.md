# Manufacturing Analytics Platform

A portfolio project demonstrating end-to-end data engineering capabilities for manufacturing analytics, built to strengthen candidacy for US-based Data Engineer and Analytics Engineer positions.

## Project Overview

This project showcases:
- Data ingestion and source-data preservation
- Data quality validation with automated tests
- Cloud data warehousing with Snowflake
- SQL transformations and analytical modeling
- dbt models, tests, and documentation
- Reproducible development workflows
- Business-oriented manufacturing analytics

## Dataset

**UCI AI4I 2020 Predictive Maintenance Dataset**

- Source: [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)
- DOI: https://doi.org/10.24432/C5HS5C
- License: CC BY 4.0

This is a synthetic industrial dataset designed for predictive maintenance research, containing 10,000 machine operation records with sensor readings and failure indicators.

See [docs/DATASET.md](docs/DATASET.md) for detailed dataset documentation.

## Architecture

```
UCI Dataset → Python Ingestion → Raw Data Storage → Snowflake Raw Tables
    → Staging Transformations → dbt Analytical Models → Business Analytics
```

### Snowflake Schemas
- `RAW` - Source data as loaded
- `STAGING` - Cleaned and standardized data
- `ANALYTICS` - Business-ready analytical models

## Project Structure

```
manufacturing-analytics-platform/
├── data/
│   └── raw/                    # Raw data files and manifest
├── ingestion/
│   ├── inspect_dataset.py      # Dataset download and profiling
│   ├── create_manifest.py      # Manifest generation
│   ├── snowflake_loader.py     # Programmatic Snowflake data loading
│   └── generate_keys.py        # RSA key pair generation for auth
├── sql/                        # Snowflake SQL scripts
│   ├── 00_git_integration.sql  # Snowflake-GitHub integration setup
│   ├── 01_setup_database.sql   # Database and schema creation
│   ├── 02_create_raw_objects.sql
│   ├── 03_load_raw_data.sql
│   └── 04_validate_raw_data.sql
├── tests/
│   └── test_raw_data.py        # Data quality tests
├── docs/
│   └── DATASET.md              # Dataset documentation
├── dbt_project/                # dbt transformation layer
│   ├── models/
│   │   ├── staging/            # Data cleaning & standardization
│   │   ├── intermediate/       # Business logic transformations
│   │   └── marts/              # Analytics-ready tables
│   ├── macros/                 # Reusable SQL functions
│   ├── tests/                  # Custom data tests
│   └── seeds/                  # Reference data
├── requirements.txt            # Python dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+
- pip or conda for package management
- Snowflake account (free trial available)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/antimoh/manufacturing-analytics-platform.git
   cd manufacturing-analytics-platform
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Data Ingestion

1. Download and inspect the dataset:
   ```bash
   python ingestion/inspect_dataset.py
   ```

2. Create the data manifest:
   ```bash
   python ingestion/create_manifest.py
   ```

3. Run data quality tests:
   ```bash
   pytest tests/test_raw_data.py -v
   ```

### Snowflake Setup

1. Generate RSA key pair for authentication:
   ```bash
   python ingestion/generate_keys.py
   ```

2. Register the public key in Snowflake (see output from step 1)

3. Set environment variables:
   ```powershell
   $env:SNOWFLAKE_ACCOUNT = "ORGNAME-ACCOUNTNAME"
   $env:SNOWFLAKE_USER = "your_login_name@email.com"
   ```

4. Load data to Snowflake:
   ```bash
   python ingestion/snowflake_loader.py
   ```

### dbt Transformation Layer

1. Install dbt-snowflake:
   ```bash
   pip install dbt-snowflake>=1.7.0
   ```

2. Install dbt packages:
   ```bash
   cd dbt_project
   dbt deps
   ```

3. Run dbt models:
   ```bash
   dbt build  # Runs models and tests
   ```

4. Generate documentation:
   ```bash
   dbt docs generate
   dbt docs serve
   ```

See [dbt_project/README.md](dbt_project/README.md) for detailed dbt documentation.

## Business Questions

This project explores:
1. What is the overall machine failure rate?
2. Which machine types have higher failure rates?
3. How do operating conditions relate to failure occurrence?
4. Which failure modes are most common?
5. How do tool wear, torque, and rotational speed relate to failure patterns?

## Roadmap

- [x] Phase 1: Local data engineering foundations
- [x] Phase 2: Snowflake setup and data loading
  - [x] Database, schemas, warehouse created
  - [x] Snowflake Git Integration configured
  - [x] Python data loader with key-pair authentication
  - [x] Raw data loaded and validated (10,000 rows, 339 failures)
- [x] Phase 3: dbt implementation
  - [x] Staging models with source definitions
  - [x] Intermediate models with business logic
  - [x] Marts models (fact & dimension tables)
  - [x] Custom macros and tests
  - [x] Documentation and freshness checks
- [ ] Phase 4: Dashboard and visualization
- [ ] Phase 5: Portfolio refinement

## Technologies

- **Languages:** Python, SQL
- **Data Warehouse:** Snowflake
- **Transformation:** dbt
- **Testing:** pytest, dbt tests
- **Version Control:** Git
- **Integration:** Snowflake Git Integration (execute SQL directly from GitHub)
- **Authentication:** RSA key-pair authentication (enterprise-grade security)

## License

This project is for educational and portfolio purposes. The dataset is licensed under CC BY 4.0.

## Attribution

Dataset citation:
> UCI Machine Learning Repository. AI4I 2020 Predictive Maintenance Dataset.
> https://doi.org/10.24432/C5HS5C
