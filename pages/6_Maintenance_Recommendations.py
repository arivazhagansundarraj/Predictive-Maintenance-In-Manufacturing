"""
pages/6_Maintenance_Recommendations.py
Batch maintenance recommendation engine with ranking, color coding,
downloadable CSV reports, and health score analysis.
"""

import os
import sys
import io
import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.data_processing import (
    load_raw_data, clean_data, engineer_features,
    FEATURE_COLS, TARGET_COL,
)
from src.model_training import load_best_model, load_scaler
from src.anomaly_detection import load_isolation_forest, predict_anomaly
from src.health_score import batch_health_scores
from src.recommendation import get_recommendation, get_recommendation_label, get_recommendation_color

st.set_page_config(page_title="Maintenance Recommendations — PredictIQ", page_icon="🔧", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.section-title{font-size:1.3rem;font-weight:700;color:#00D4FF;margin-bottom:0.8rem;}
.metric-card{background:linear-gradient(135deg,#1A2236,#0D1526);border:1px solid rgba(0,212,255,0.15);
  border-radius:16px;padding:1.25rem 1.5rem;margin-bottom:0.5rem;}
</style>""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(26,34,54,0.5)",
    font_color="#E2E8F0",
)

st.markdown('<h1 class="section-title" style="font-size:2rem;">🔧 Maintenance Recommendation Panel</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#94A3B8;margin-top:-0.5rem;">Batch analysis and ranked maintenance scheduling across the entire fleet</p>', unsafe_allow_html=True)

@st.cache_resource
def load_all():
    model = load_best_model()
    scaler = load_scaler()
    iso = load_isolation_forest()
    return model, scaler, iso

@st.cache_data
def load_dataset():
    df_raw = load_raw_data()
    df_clean = clean_data(df_raw)
    return engineer_features(df_clean)

model, scaler, iso = load_all()

# ── Source selector ────────────────────────────────────────────────────────
source = st.radio("Data Source", ["📋 Full AI4I Dataset", "📁 Upload CSV"], horizontal=True)
st.markdown("---")

if source == "📁 Upload CSV":
    uploaded = st.file_uploader("Upload CSV (AI4I format)", type=["csv"])
    if not uploaded:
        st.info("Upload a CSV file to begin batch analysis.")
        st.stop()
    df_raw_up = pd.read_csv(uploaded)
    try:
        df_clean_up = clean_data(df_raw_up)
        df_feat = engineer_features(df_clean_up)
        st.success(f"Loaded {len(df_feat):,} records from uploaded file.")
    except Exception as e:
        st.error(f"Error processing file: {e}")
        st.stop()
else:
    df_feat = load_dataset()
    st.success(f"Loaded {len(df_feat):,} records from AI4I 2020 dataset.")

# ── Scoring ────────────────────────────────────────────────────────────────
with st.spinner("Computing health scores and recommendations..."):
    X_all = scaler.transform(df_feat[FEATURE_COLS].values)
    failure_probs = model.predict_proba(X_all)[:, 1]
    _, _, anomaly_norm = predict_anomaly(iso, X_all)
    health_scores = batch_health_scores(failure_probs, anomaly_norm, df_feat[FEATURE_COLS])

    rec_names = [get_recommendation(s)["name"] for s in health_scores]
    rec_labels = [get_recommendation_label(s) for s in health_scores]
    rec_colors = [get_recommendation_color(s) for s in health_scores]
    priorities = [get_recommendation(s)["priority"] for s in health_scores]

# Build results DataFrame
df_results = df_feat[FEATURE_COLS].copy()
df_results.insert(0, "Machine #", range(1, len(df_results) + 1))
df_results["Health Score"] = np.round(health_scores, 2)
df_results["Failure Prob (%)"] = np.round(failure_probs * 100, 2)
df_results["Anomaly Score (%)"] = np.round(anomaly_norm * 100, 2)
df_results["Recommendation"] = rec_labels
df_results["Priority"] = priorities

# Sort by health score ascending (worst first)
df_results = df_results.sort_values("Health Score", ascending=True).reset_index(drop=True)

# ── Summary KPIs ───────────────────────────────────────────────────────────
from collections import Counter
cat_counts = Counter(rec_names)
c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    ("🔴 Immediate", cat_counts.get("Immediate Maintenance", 0), "#FF4B4B"),
    ("🟠 Schedule", cat_counts.get("Schedule Maintenance", 0), "#FF8C00"),
    ("🟡 Monitor", cat_counts.get("Monitor Closely", 0), "#FFD700"),
    ("🟢 Healthy", cat_counts.get("Healthy", 0), "#00D4FF"),
    ("💚 Avg Health", f"{health_scores.mean():.1f}", "#00FF88"),
]
for col, (lbl, val, color) in zip([c1, c2, c3, c4, c5], kpis):
    col.markdown(f"""
<div class="metric-card" style="text-align:center;">
  <div style="font-size:0.7rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.1em;">{lbl}</div>
  <div style="font-size:2rem;font-weight:800;color:{color};">{val}</div>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Health Score Timeline ──────────────────────────────────────────────────
col_chart, col_pie = st.columns([3, 2])

with col_chart:
    st.markdown('<div class="section-title">Health Score — Ranked Fleet View</div>', unsafe_allow_html=True)
    sample_n = min(500, len(df_results))
    df_plot = df_results.head(sample_n)

    color_map = {
        "🔴 Immediate Maintenance": "#FF4B4B",
        "🟠 Schedule Maintenance": "#FF8C00",
        "🟡 Monitor Closely": "#FFD700",
        "🟢 Healthy": "#00D4FF",
    }

    fig_line = go.Figure()
    for cat, color in [
        ("Immediate Maintenance", "#FF4B4B"),
        ("Schedule Maintenance", "#FF8C00"),
        ("Monitor Closely", "#FFD700"),
        ("Healthy", "#00D4FF"),
    ]:
        mask = [cat in r for r in df_plot["Recommendation"].tolist()]
        if any(mask):
            idx = [i for i, m in enumerate(mask) if m]
            fig_line.add_trace(go.Scatter(
                x=[i+1 for i in idx],
                y=df_plot["Health Score"].iloc[idx],
                mode="markers",
                name=cat,
                marker=dict(color=color, size=5, opacity=0.7),
            ))
    for thresh, color, label in [(40, "#FF4B4B", "Critical"), (60, "#FF8C00", "Warning"), (80, "#FFD700", "Monitor")]:
        fig_line.add_hline(y=thresh, line_dash="dot", line_color=color, opacity=0.5,
                           annotation_text=label, annotation_font_color=color)
    fig_line.update_layout(
        **PLOTLY_LAYOUT, height=350,
        xaxis_title="Machine Rank (worst to best)",
        yaxis_title="Health Score",
        legend=dict(font=dict(color="#E2E8F0", size=10), bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_pie:
    st.markdown('<div class="section-title">Fleet Status Distribution</div>', unsafe_allow_html=True)
    cat_order = ["Immediate Maintenance", "Schedule Maintenance", "Monitor Closely", "Healthy"]
    cat_colors = ["#FF4B4B", "#FF8C00", "#FFD700", "#00D4FF"]
    cat_vals = [cat_counts.get(c, 0) for c in cat_order]

    fig_pie = go.Figure(go.Pie(
        labels=cat_order, values=cat_vals,
        marker=dict(colors=cat_colors),
        textinfo="label+percent",
        textfont=dict(color="#E2E8F0"),
        hole=0.45,
    ))
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_color="#E2E8F0", height=350,
        legend=dict(font=dict(color="#E2E8F0", size=10), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=20, b=20, l=20, r=20),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Health Score Distribution by Type ──────────────────────────────────────
if "Type" in df_feat.columns:
    st.markdown('<div class="section-title">Health Score by Product Type</div>', unsafe_allow_html=True)
    type_map_rev = {0: "L", 1: "M", 2: "H"}
    df_box = df_feat[["Type"]].copy()
    df_box["Health Score"] = health_scores
    df_box["Type Label"] = df_box["Type"].map(type_map_rev)
    fig_box = px.box(
        df_box, x="Type Label", y="Health Score",
        color="Type Label",
        color_discrete_map={"L": "#FF4B4B", "M": "#FFD700", "H": "#00D4FF"},
        points="outliers",
    )
    fig_box.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

# ── Ranked Machine Table ───────────────────────────────────────────────────
st.markdown('<div class="section-title">🏭 Fleet Maintenance Schedule (Ranked)</div>', unsafe_allow_html=True)

filter_cat = st.multiselect(
    "Filter by Recommendation",
    options=["🔴 Immediate Maintenance", "🟠 Schedule Maintenance", "🟡 Monitor Closely", "🟢 Healthy"],
    default=["🔴 Immediate Maintenance", "🟠 Schedule Maintenance"],
)

df_display = df_results.copy()
if filter_cat:
    df_display = df_display[df_display["Recommendation"].isin(filter_cat)]

# Add color styling to table
def color_rec(val):
    cmap = {
        "🔴 Immediate Maintenance": "background-color:rgba(255,75,75,0.15);color:#FF4B4B",
        "🟠 Schedule Maintenance": "background-color:rgba(255,140,0,0.15);color:#FF8C00",
        "🟡 Monitor Closely": "background-color:rgba(255,215,0,0.15);color:#FFD700",
        "🟢 Healthy": "background-color:rgba(0,212,255,0.15);color:#00D4FF",
    }
    return cmap.get(val, "")

def color_health(val):
    if val < 40:
        return "color:#FF4B4B;font-weight:bold"
    elif val < 60:
        return "color:#FF8C00;font-weight:bold"
    elif val < 80:
        return "color:#FFD700"
    return "color:#00D4FF"

display_cols = ["Machine #", "Health Score", "Failure Prob (%)", "Anomaly Score (%)",
                "Recommendation", "Priority"] + [c for c in FEATURE_COLS[:5] if c in df_display.columns]

styler = df_display[display_cols].head(200).style
if hasattr(styler, "map"):
    styler = styler.map(color_rec, subset=["Recommendation"]).map(color_health, subset=["Health Score"])
else:
    styler = styler.applymap(color_rec, subset=["Recommendation"]).applymap(color_health, subset=["Health Score"])

st.dataframe(
    styler,
    use_container_width=True, height=450,
)

# ── Download ───────────────────────────────────────────────────────────────
st.markdown("---")
col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    csv_all = io.StringIO()
    df_results.to_csv(csv_all, index=False)
    st.download_button(
        "⬇️ Download Full Fleet Report (CSV)",
        data=csv_all.getvalue().encode("utf-8"),
        file_name=f"fleet_maintenance_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )

with col_dl2:
    critical_only = df_results[df_results["Recommendation"].str.contains("Immediate|Schedule")]
    csv_crit = io.StringIO()
    critical_only.to_csv(csv_crit, index=False)
    st.download_button(
        "⬇️ Download Critical & Urgent Only (CSV)",
        data=csv_crit.getvalue().encode("utf-8"),
        file_name=f"critical_maintenance_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )

st.markdown(f"""
<div style="text-align:center;color:#64748B;font-size:0.75rem;margin-top:1rem;">
  Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
  Total records scored: {len(df_results):,} |
  Model: {load_best_model().__class__.__name__}
</div>""", unsafe_allow_html=True)
