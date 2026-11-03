# Manufacturing Analytics Dashboard

Interactive Streamlit dashboard for predictive maintenance insights.

## 🚀 Live Demo

**[View Live Dashboard](https://mfg-analytics-platform.streamlit.app)**

## Features

- **KPI Metrics**: Total readings, failures, and maintenance priorities
- **Failure Analysis**: Breakdown by machine type and failure mode
- **Operating Conditions**: Temperature, power, and tool wear visualizations
- **Predictive Indicators**: Risk assessment and model validation
- **Interactive Filters**: Filter by machine type and risk level

## Local Development

```bash
# From project root
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

## Data

The dashboard uses pre-exported data from Snowflake mart tables:
- `dim_machine_types.csv` - Machine type reference
- `fct_failure_events.csv` - All sensor readings with analysis
- `fct_failure_summary.csv` - Aggregated failure statistics
- `fct_machine_performance.csv` - Performance by type/risk
- `fct_predictive_indicators.csv` - Predictive maintenance flags

## Deployment

This app is deployed on [Streamlit Community Cloud](https://streamlit.io/cloud).

To deploy your own:
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select the repository and `streamlit_app/app.py`
5. Click Deploy

## Screenshots

*Coming soon*

## Technologies

- **Streamlit** - Dashboard framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation

## Author

Anton Timokhin - [GitHub](https://github.com/antimoh)
