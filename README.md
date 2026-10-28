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
│   └── create_manifest.py      # Manifest generation
├── sql/                        # SQL transformations (coming soon)
├── tests/
│   └── test_raw_data.py        # Data quality tests
├── docs/
│   └── DATASET.md              # Dataset documentation
├── dbt_project/                # dbt models (coming soon)
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

The dataset is downloaded from UCI Machine Learning Repository using the provided scripts:

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

## Business Questions

This project explores:
1. What is the overall machine failure rate?
2. Which machine types have higher failure rates?
3. How do operating conditions relate to failure occurrence?
4. Which failure modes are most common?
5. How do tool wear, torque, and rotational speed relate to failure patterns?

## Roadmap

- [x] Phase 1: Local data engineering foundations
- [ ] Phase 2: Snowflake setup and data loading
- [ ] Phase 3: SQL modeling and analytics
- [ ] Phase 4: dbt implementation
- [ ] Phase 5: Portfolio quality and documentation

## Technologies

- **Languages:** Python, SQL
- **Data Warehouse:** Snowflake
- **Transformation:** dbt
- **Testing:** pytest, dbt tests
- **Version Control:** Git

## License

This project is for educational and portfolio purposes. The dataset is licensed under CC BY 4.0.

## Attribution

Dataset citation:
> UCI Machine Learning Repository. AI4I 2020 Predictive Maintenance Dataset.
> https://doi.org/10.24432/C5HS5C
