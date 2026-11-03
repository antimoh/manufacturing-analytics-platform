"""
Manufacturing Analytics Dashboard
==================================

Interactive dashboard for predictive maintenance insights.
Built with Streamlit, designed for portfolio demonstration.

Author: Anton Timokhin
Data Source: UCI AI4I 2020 Predictive Maintenance Dataset
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Manufacturing Analytics | Predictive Maintenance",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data
def load_data():
    """Load all mart tables from CSV files."""
    data_dir = Path(__file__).parent / "data"
    
    data = {
        "dim_machine_types": pd.read_csv(data_dir / "dim_machine_types.csv"),
        "fct_failure_events": pd.read_csv(data_dir / "fct_failure_events.csv"),
        "fct_failure_summary": pd.read_csv(data_dir / "fct_failure_summary.csv"),
        "fct_machine_performance": pd.read_csv(data_dir / "fct_machine_performance.csv"),
        "fct_predictive_indicators": pd.read_csv(data_dir / "fct_predictive_indicators.csv"),
    }
    
    return data


# Load data
data = load_data()
dim_machine = data["dim_machine_types"]
fct_events = data["fct_failure_events"]
fct_summary = data["fct_failure_summary"]
fct_performance = data["fct_machine_performance"]
fct_predictive = data["fct_predictive_indicators"]

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/factory.png", width=80)
    st.title("Manufacturing Analytics")
    st.markdown("---")
    
    # Machine type filter
    machine_types = ["All"] + list(dim_machine["machine_type"].unique())
    selected_machine = st.selectbox(
        "🔧 Filter by Machine Type",
        machine_types,
        help="L=Low Quality, M=Medium Quality, H=High Quality"
    )
    
    # Risk level filter
    risk_levels = ["All"] + ["High", "Medium", "Low", "Minimal"]
    selected_risk = st.selectbox(
        "⚠️ Filter by Risk Level",
        risk_levels
    )
    
    st.markdown("---")
    st.markdown("### About This Dashboard")
    st.markdown("""
    This dashboard analyzes machine sensor data 
    to predict maintenance needs and prevent failures.
    
    **Data:** 10,000 machine operation records  
    **Source:** UCI ML Repository  
    **Built with:** Python, dbt, Snowflake, Streamlit
    """)
    
    st.markdown("---")
    st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-Repo-blue?logo=github)](https://github.com/antimoh/manufacturing-analytics-platform)")

# =============================================================================
# FILTER DATA
# =============================================================================

# Apply filters to main dataset
filtered_events = fct_events.copy()
filtered_predictive = fct_predictive.copy()

if selected_machine != "All":
    filtered_events = filtered_events[filtered_events["machine_type"] == selected_machine]
    filtered_predictive = filtered_predictive[filtered_predictive["machine_type"] == selected_machine]

if selected_risk != "All":
    filtered_events = filtered_events[filtered_events["risk_level"] == selected_risk]
    filtered_predictive = filtered_predictive[filtered_predictive["risk_level"] == selected_risk]

# =============================================================================
# HEADER
# =============================================================================

st.title("🏭 Predictive Maintenance Dashboard")
st.markdown("Real-time insights for manufacturing equipment health and failure prevention")

# =============================================================================
# KPI METRICS
# =============================================================================

st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

total_readings = len(filtered_events)
total_failures = filtered_events["is_machine_failure"].sum()
failure_rate = (total_failures / total_readings * 100) if total_readings > 0 else 0

# Predictive metrics
immediate_maintenance = len(filtered_predictive[filtered_predictive["maintenance_priority"] == "IMMEDIATE"])
urgent_maintenance = len(filtered_predictive[filtered_predictive["maintenance_priority"] == "URGENT"])

with col1:
    st.metric(
        label="Total Readings",
        value=f"{total_readings:,}",
        help="Number of machine sensor readings"
    )

with col2:
    st.metric(
        label="Total Failures",
        value=f"{int(total_failures):,}",
        delta=f"{failure_rate:.1f}% failure rate",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="🚨 Immediate Action",
        value=f"{immediate_maintenance:,}",
        help="Machines requiring immediate maintenance"
    )

with col4:
    st.metric(
        label="⚡ Urgent Review",
        value=f"{urgent_maintenance:,}",
        help="Machines requiring urgent attention"
    )

with col5:
    high_risk = len(filtered_events[filtered_events["risk_level"] == "High"])
    st.metric(
        label="⚠️ High Risk",
        value=f"{high_risk:,}",
        help="Readings classified as high risk"
    )

# =============================================================================
# ROW 1: FAILURE ANALYSIS
# =============================================================================

st.markdown("---")
st.subheader("📊 Failure Analysis")

col1, col2 = st.columns(2)

with col1:
    # Failure rate by machine type
    fig_failure_rate = px.bar(
        dim_machine,
        x="machine_type_description",
        y="failure_rate_pct",
        color="machine_type",
        title="Failure Rate by Machine Type",
        labels={
            "machine_type_description": "Machine Type",
            "failure_rate_pct": "Failure Rate (%)",
            "machine_type": "Type"
        },
        color_discrete_map={"L": "#EF553B", "M": "#FECB52", "H": "#00CC96"}
    )
    fig_failure_rate.update_layout(showlegend=False)
    st.plotly_chart(fig_failure_rate, use_container_width=True)

with col2:
    # Failure type distribution
    failure_types = fct_summary.groupby("primary_failure_type")["event_count"].sum().reset_index()
    failure_types = failure_types.sort_values("event_count", ascending=True)
    
    fig_failure_types = px.bar(
        failure_types,
        x="event_count",
        y="primary_failure_type",
        orientation="h",
        title="Failure Type Distribution",
        labels={
            "event_count": "Number of Failures",
            "primary_failure_type": "Failure Type"
        },
        color="event_count",
        color_continuous_scale="Reds"
    )
    fig_failure_types.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig_failure_types, use_container_width=True)

# =============================================================================
# ROW 2: OPERATING CONDITIONS
# =============================================================================

st.markdown("---")
st.subheader("🌡️ Operating Conditions Analysis")

col1, col2 = st.columns(2)

with col1:
    # Temperature vs Power scatter
    sample_data = filtered_events.sample(min(1000, len(filtered_events)), random_state=42)
    
    fig_scatter = px.scatter(
        sample_data,
        x="power_watts",
        y="temperature_differential_k",
        color="is_machine_failure",
        title="Temperature Differential vs Power Output",
        labels={
            "power_watts": "Power (Watts)",
            "temperature_differential_k": "Temp Differential (K)",
            "is_machine_failure": "Failure"
        },
        color_discrete_map={0: "#636EFA", 1: "#EF553B"},
        opacity=0.6
    )
    fig_scatter.update_layout(
        legend_title_text="Machine Failure",
        legend=dict(
            itemsizing="constant",
            title_font_size=12,
        )
    )
    # Add reference lines for failure thresholds
    fig_scatter.add_hline(y=8.6, line_dash="dash", line_color="red", 
                          annotation_text="HDF Threshold (8.6K)")
    fig_scatter.add_vline(x=3500, line_dash="dash", line_color="orange",
                          annotation_text="Min Power")
    fig_scatter.add_vline(x=9000, line_dash="dash", line_color="orange",
                          annotation_text="Max Power")
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    # Tool wear distribution by failure status
    fig_wear = px.histogram(
        filtered_events,
        x="tool_wear_minutes",
        color="is_machine_failure",
        title="Tool Wear Distribution by Failure Status",
        labels={
            "tool_wear_minutes": "Tool Wear (minutes)",
            "is_machine_failure": "Failure",
            "count": "Count"
        },
        color_discrete_map={0: "#636EFA", 1: "#EF553B"},
        barmode="overlay",
        opacity=0.7
    )
    fig_wear.add_vline(x=200, line_dash="dash", line_color="red",
                       annotation_text="TWF Zone Start")
    fig_wear.update_layout(legend_title_text="Machine Failure")
    st.plotly_chart(fig_wear, use_container_width=True)

# =============================================================================
# ROW 3: PREDICTIVE INDICATORS
# =============================================================================

st.markdown("---")
st.subheader("🔮 Predictive Maintenance Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    # Maintenance priority distribution
    priority_counts = filtered_predictive["maintenance_priority"].value_counts().reset_index()
    priority_counts.columns = ["priority", "count"]
    
    # Define order
    priority_order = ["IMMEDIATE", "URGENT", "SCHEDULED", "MONITOR", "NORMAL"]
    priority_counts["priority"] = pd.Categorical(
        priority_counts["priority"], 
        categories=priority_order, 
        ordered=True
    )
    priority_counts = priority_counts.sort_values("priority")
    
    fig_priority = px.pie(
        priority_counts,
        values="count",
        names="priority",
        title="Maintenance Priority Distribution",
        color="priority",
        color_discrete_map={
            "IMMEDIATE": "#EF553B",
            "URGENT": "#FFA15A",
            "SCHEDULED": "#FECB52",
            "MONITOR": "#00CC96",
            "NORMAL": "#636EFA"
        }
    )
    fig_priority.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_priority, use_container_width=True)

with col2:
    # Risk indicator heatmap
    risk_data = pd.DataFrame({
        "Indicator": ["HDF Risk", "PWF Risk", "TWF Risk", "OSF Risk"],
        "HIGH": [
            len(filtered_predictive[filtered_predictive["hdf_risk_indicator"] == "HIGH"]),
            len(filtered_predictive[filtered_predictive["pwf_risk_indicator"] == "HIGH"]),
            len(filtered_predictive[filtered_predictive["twf_risk_indicator"].isin(["HIGH", "CRITICAL"])]),
            len(filtered_predictive[filtered_predictive["osf_risk_indicator"].isin(["HIGH", "CRITICAL"])]),
        ],
        "MEDIUM": [
            len(filtered_predictive[filtered_predictive["hdf_risk_indicator"] == "MEDIUM"]),
            len(filtered_predictive[filtered_predictive["pwf_risk_indicator"] == "MEDIUM"]),
            len(filtered_predictive[filtered_predictive["twf_risk_indicator"] == "MEDIUM"]),
            len(filtered_predictive[filtered_predictive["osf_risk_indicator"] == "MEDIUM"]),
        ],
    })
    
    fig_risk = px.bar(
        risk_data,
        x="Indicator",
        y=["HIGH", "MEDIUM"],
        title="Risk Indicators Summary",
        barmode="group",
        color_discrete_map={"HIGH": "#EF553B", "MEDIUM": "#FECB52"}
    )
    fig_risk.update_layout(
        legend_title_text="Risk Level",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_risk, use_container_width=True)

with col3:
    # Model validation metrics
    total_actual = filtered_predictive["is_machine_failure"].sum()
    true_pos = filtered_predictive["true_positive"].sum()
    false_pos = filtered_predictive["false_positive"].sum()
    false_neg = filtered_predictive["false_negative"].sum()
    
    precision = true_pos / (true_pos + false_pos) * 100 if (true_pos + false_pos) > 0 else 0
    recall = true_pos / (true_pos + false_neg) * 100 if (true_pos + false_neg) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    fig_metrics = go.Figure()
    
    fig_metrics.add_trace(go.Indicator(
        mode="gauge+number",
        value=recall,
        title={"text": "Model Recall (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#00CC96"},
            "steps": [
                {"range": [0, 50], "color": "#FFCCCB"},
                {"range": [50, 75], "color": "#FFEFD5"},
                {"range": [75, 100], "color": "#90EE90"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 50
            }
        }
    ))
    
    fig_metrics.update_layout(
        title="Predictive Model Performance",
        height=300
    )
    st.plotly_chart(fig_metrics, use_container_width=True)
    
    # Show precision and F1 as text
    st.markdown(f"""
    **Model Metrics:**
    - Precision: **{precision:.1f}%**
    - Recall: **{recall:.1f}%**
    - F1 Score: **{f1:.1f}%**
    """)

# =============================================================================
# ROW 4: PERFORMANCE BY RISK LEVEL
# =============================================================================

st.markdown("---")
st.subheader("📈 Performance Analysis by Risk Level")

col1, col2 = st.columns(2)

with col1:
    # Failure rate by risk level
    risk_failure = fct_performance.groupby("risk_level").agg({
        "reading_count": "sum",
        "failure_count": "sum"
    }).reset_index()
    risk_failure["failure_rate"] = risk_failure["failure_count"] / risk_failure["reading_count"] * 100
    
    # Order risk levels
    risk_order = ["Minimal", "Low", "Medium", "High"]
    risk_failure["risk_level"] = pd.Categorical(
        risk_failure["risk_level"],
        categories=risk_order,
        ordered=True
    )
    risk_failure = risk_failure.sort_values("risk_level")
    
    fig_risk_failure = px.bar(
        risk_failure,
        x="risk_level",
        y="failure_rate",
        title="Failure Rate by Risk Level",
        labels={
            "risk_level": "Risk Level",
            "failure_rate": "Failure Rate (%)"
        },
        color="failure_rate",
        color_continuous_scale="Reds"
    )
    fig_risk_failure.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_risk_failure, use_container_width=True)

with col2:
    # Average metrics by machine type
    metrics_by_type = dim_machine[["machine_type_description", "avg_torque_nm", 
                                    "avg_rotational_speed_rpm", "avg_tool_wear_minutes"]].copy()
    metrics_by_type = metrics_by_type.melt(
        id_vars=["machine_type_description"],
        var_name="Metric",
        value_name="Value"
    )
    metrics_by_type["Metric"] = metrics_by_type["Metric"].replace({
        "avg_torque_nm": "Avg Torque (Nm)",
        "avg_rotational_speed_rpm": "Avg Speed (RPM/100)",
        "avg_tool_wear_minutes": "Avg Tool Wear (min)"
    })
    # Scale RPM for visibility
    metrics_by_type.loc[metrics_by_type["Metric"] == "Avg Speed (RPM/100)", "Value"] /= 100
    
    fig_metrics_type = px.bar(
        metrics_by_type,
        x="machine_type_description",
        y="Value",
        color="Metric",
        title="Operating Metrics by Machine Type",
        barmode="group",
        labels={
            "machine_type_description": "Machine Type",
            "Value": "Value"
        }
    )
    st.plotly_chart(fig_metrics_type, use_container_width=True)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>Built by <strong>Anton Timokhin</strong> | 
    <a href='https://github.com/antimoh/manufacturing-analytics-platform'>GitHub Repository</a> | 
    Data: UCI AI4I 2020 Predictive Maintenance Dataset</p>
    <p>Technologies: Python • dbt • Snowflake • Streamlit • Plotly</p>
</div>
""", unsafe_allow_html=True)
