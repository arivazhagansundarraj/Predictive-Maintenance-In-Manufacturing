"""
pages/2_Dataset_Insights.py
Exploratory data analysis: distributions, correlations, SMOTE comparison.
"""

import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.data_processing import load_raw_data, clean_data, engineer_features, FEATURE_COLS, TARGET_COL

st.set_page_config(page_title="Dataset Insights — PredictIQ", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.section-title{font-size:1.3rem;font-weight:700;color:#00D4FF;margin-bottom:0.8rem;}
.metric-card{background:linear-gradient(135deg,#1A2236,#0D1526);border:1px solid rgba(0,212,255,0.15);
  border-radius:16px;padding:1rem 1.5rem;margin-bottom:0.5rem;}
</style>""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(26,34,54,0.5)",
    font_color="#E2E8F0",
)

st.markdown('<h1 class="section-title" style="font-size:2rem;">📊 Dataset Insights</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#94A3B8;margin-top:-0.5rem;">AI4I 2020 Predictive Maintenance Dataset — Exploratory Analysis</p>', unsafe_allow_html=True)

@st.cache_data
def get_data():
    df_raw = load_raw_data()
    df_clean = clean_data(df_raw)
    df_feat = engineer_features(df_clean)
    return df_raw, df_clean, df_feat

df_raw, df_clean, df_feat = get_data()

# ── Quick stats ────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
stats = [
    ("📋 Total Records", f"{len(df_raw):,}"),
    ("📌 Features", f"{len(df_feat.columns)}"),
    ("⚠️ Failure Rate", f"{df_feat[TARGET_COL].mean()*100:.2f}%"),
    ("🔧 Engineered Features", "3 new"),
]
for col, (label, val) in zip([c1, c2, c3, c4], stats):
    col.markdown(f"""
<div class="metric-card" style="text-align:center;">
  <div style="font-size:0.75rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.1em;">{label}</div>
  <div style="font-size:2rem;font-weight:800;color:#00D4FF;">{val}</div>
</div>""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Raw Data", "📈 Distributions", "🔥 Correlations", "⚖️ Class Balance", "🧬 Feature Engineering"
])

with tab1:
    st.markdown('<div class="section-title">Dataset Preview</div>', unsafe_allow_html=True)
    st.dataframe(
        df_raw.head(50).style.background_gradient(
            subset=["Air temperature [K]", "Process temperature [K]", "Torque [Nm]", "Tool wear [min]"],
            cmap="Blues",
        ),
        use_container_width=True, height=400,
    )
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">Descriptive Statistics</div>', unsafe_allow_html=True)
        st.dataframe(df_feat[FEATURE_COLS].describe().round(3), use_container_width=True)
    with col_r:
        st.markdown('<div class="section-title">Missing Values & Dtypes</div>', unsafe_allow_html=True)
        info_df = pd.DataFrame({
            "Column": df_raw.columns,
            "Dtype": df_raw.dtypes.astype(str).values,
            "Missing": df_raw.isnull().sum().values,
            "Missing %": (df_raw.isnull().mean() * 100).round(2).values,
        })
        st.dataframe(info_df, use_container_width=True)

with tab2:
    st.markdown('<div class="section-title">Sensor Feature Distributions (by Failure)</div>', unsafe_allow_html=True)
    sensor_cols = ["Air temperature [K]", "Process temperature [K]", "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"]
    n = len(sensor_cols)
    fig_dist = make_subplots(rows=2, cols=3, subplot_titles=sensor_cols + [""])
    positions = [(1,1),(1,2),(1,3),(2,1),(2,2)]
    colors_fail = {0: "#00D4FF", 1: "#FF4B4B"}
    for idx, (col_name, pos) in enumerate(zip(sensor_cols, positions)):
        for fail_val in [0, 1]:
            subset = df_feat[df_feat[TARGET_COL] == fail_val][col_name]
            fig_dist.add_trace(
                go.Histogram(x=subset, name=f"{'Failure' if fail_val else 'Normal'}",
                             opacity=0.7, marker_color=colors_fail[fail_val],
                             showlegend=(idx == 0), legendgroup=str(fail_val)),
                row=pos[0], col=pos[1],
            )
    fig_dist.update_layout(**PLOTLY_LAYOUT, height=500, barmode="overlay", margin=dict(t=40, b=40, l=50, r=30),
                           legend=dict(x=0.75, y=0.15))
    st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown('<div class="section-title">Product Type Distribution</div>', unsafe_allow_html=True)
    type_counts = df_raw["Type"].value_counts()
    fig_type = px.bar(
        x=type_counts.index, y=type_counts.values,
        labels={"x": "Product Type", "y": "Count"},
        color=type_counts.index,
        color_discrete_map={"L": "#FF4B4B", "M": "#FFD700", "H": "#00D4FF"},
        text=type_counts.values,
    )
    fig_type.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False, margin=dict(t=40, b=40, l=50, r=30))
    st.plotly_chart(fig_type, use_container_width=True)

with tab3:
    st.markdown('<div class="section-title">Feature Correlation Heatmap</div>', unsafe_allow_html=True)
    numeric_cols = [c for c in df_feat.columns if df_feat[c].dtype in [np.float64, np.int64, float, int]]
    corr = df_feat[numeric_cols].corr()
    fig_hm = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index,
        colorscale="RdBu_r", zmid=0,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=9, color="#E2E8F0"),
        colorbar=dict(tickcolor="#E2E8F0", tickfont=dict(color="#E2E8F0")),
    ))
    fig_hm.update_layout(**PLOTLY_LAYOUT, height=600, margin=dict(t=30, b=100, l=120, r=30))
    st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown('<div class="section-title">Scatter Matrix (Sensor Variables)</div>', unsafe_allow_html=True)
    sample = df_feat.sample(min(1500, len(df_feat)), random_state=42)
    fig_scatter = px.scatter_matrix(
        sample,
        dimensions=["Air temperature [K]", "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"],
        color=TARGET_COL,
        color_discrete_map={0: "#00D4FF", 1: "#FF4B4B"},
        labels={TARGET_COL: "Machine Failure"},
    )
    fig_scatter.update_traces(diagonal_visible=False, marker=dict(size=2, opacity=0.6))
    fig_scatter.update_layout(**PLOTLY_LAYOUT, height=550, margin=dict(t=40, b=40, l=50, r=30))
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    st.markdown('<div class="section-title">Class Imbalance — Before vs After SMOTE</div>', unsafe_allow_html=True)
    from src.model_training import load_model_metrics
    try:
        mets = load_model_metrics()
        before = mets.get("class_counts_before", {0: 9661, 1: 339})
        after = mets.get("class_counts_after", {0: 9661, 1: 9661})
    except Exception:
        before = {0: 9661, 1: 339}
        after = {0: 9661, 1: 9661}

    col_b, col_a = st.columns(2)
    for col, data, title in [(col_b, before, "Before SMOTE"), (col_a, after, "After SMOTE")]:
        with col:
            labels_pie = ["Normal (0)", "Failure (1)"]
            vals_pie = [data.get(0, data.get("0", 0)), data.get(1, data.get("1", 0))]
            fig_pie = go.Figure(go.Pie(
                labels=labels_pie, values=vals_pie,
                marker=dict(colors=["#00D4FF", "#FF4B4B"]),
                textinfo="label+percent+value",
                textfont=dict(color="#E2E8F0"),
                hole=0.4,
            ))
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#E2E8F0",
                                  height=300, title=title, legend=dict(font=dict(color="#E2E8F0")))
            st.plotly_chart(fig_pie, use_container_width=True)

    st.info("**SMOTE** (Synthetic Minority Oversampling Technique) generates synthetic failure examples in the feature space, addressing the ~3.4% failure rate imbalance without duplicating real samples.")

with tab5:
    st.markdown('<div class="section-title">Engineered Features</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    feat_info = [
        ("Temperature Difference", "Process temp − Air temp", "Measures thermal stress on the machine. Higher values indicate poor heat dissipation.", "#FF8C00"),
        ("Wear Rate", "Tool wear / Rotational speed", "Normalized wear accumulation per RPM. High values signal accelerated degradation.", "#FF4B4B"),
        ("Mechanical Load Index", "Torque × Tool wear / 1000", "Composite index of mechanical stress. Combines torque and cumulative wear.", "#FFD700"),
    ]
    for col, (name, formula, desc, color) in zip([col1, col2, col3], feat_info):
        with col:
            col.markdown(f"""
<div class="metric-card">
  <div style="font-size:0.8rem;font-weight:700;color:{color};">{name}</div>
  <div style="font-size:0.75rem;color:#94A3B8;font-family:'JetBrains Mono',monospace;margin:0.5rem 0;">{formula}</div>
  <div style="font-size:0.8rem;color:#E2E8F0;">{desc}</div>
</div>""", unsafe_allow_html=True)

    for feat in ["Temperature Difference", "Wear Rate", "Mechanical Load Index"]:
        st.markdown(f'<div class="section-title" style="margin-top:1rem;">{feat} — Distribution by Failure</div>', unsafe_allow_html=True)
        fig = px.violin(
            df_feat, x=TARGET_COL, y=feat,
            color=TARGET_COL, box=True, points="outliers",
            color_discrete_map={0: "#00D4FF", 1: "#FF4B4B"},
            labels={TARGET_COL: "Machine Failure", feat: feat},
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False, margin=dict(t=40, b=40, l=50, r=30))
        st.plotly_chart(fig, use_container_width=True)
