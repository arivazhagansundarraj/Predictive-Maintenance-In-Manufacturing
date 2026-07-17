"""
pages/1_Home_Dashboard.py
KPI overview, machine health gauges, failure distribution summary.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.data_processing import load_raw_data, clean_data, engineer_features, FEATURE_COLS, TARGET_COL
from src.model_training import load_best_model, load_scaler, load_model_metrics
from src.anomaly_detection import load_isolation_forest, predict_anomaly
from src.health_score import batch_health_scores
from src.recommendation import get_recommendation_label

st.set_page_config(page_title="Home Dashboard — PredictIQ", page_icon="🏠", layout="wide")

# ── Shared CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.metric-card {
    background: linear-gradient(135deg,#1A2236,#0D1526);
    border:1px solid rgba(0,212,255,0.15);border-radius:16px;
    padding:1.25rem 1.5rem;margin-bottom:0.5rem;
    box-shadow:0 0 20px rgba(0,212,255,0.15);
}
.kpi-value { font-size:2.2rem;font-weight:800;color:#00D4FF; }
.kpi-label { font-size:0.75rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.1em; }
.section-title { font-size:1.3rem;font-weight:700;color:#00D4FF;margin-bottom:1rem; }
div[data-testid="stMetricValue"]{font-size:1.8rem!important;font-weight:800!important;color:#00D4FF!important;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="section-title" style="font-size:2rem;">🏠 Home Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#94A3B8;margin-top:-0.5rem;">Real-time overview of manufacturing health across all machines</p>', unsafe_allow_html=True)

# ── Load data & models ─────────────────────────────────────────────────────
@st.cache_resource
def load_all():
    df_raw = load_raw_data()
    df_clean = clean_data(df_raw)
    df_feat = engineer_features(df_clean)
    model = load_best_model()
    scaler = load_scaler()
    iso = load_isolation_forest()
    metrics = load_model_metrics()
    return df_feat, model, scaler, iso, metrics

df_feat, model, scaler, iso, metrics = load_all()

X_all = scaler.transform(df_feat[FEATURE_COLS].values)
failure_probs = model.predict_proba(X_all)[:, 1]
_, _, anomaly_norm = predict_anomaly(iso, X_all)
health_scores = batch_health_scores(failure_probs, anomaly_norm, df_feat[FEATURE_COLS])
labels = [get_recommendation_label(s) for s in health_scores]

total = len(df_feat)
fail_count = int(df_feat[TARGET_COL].sum())
fail_rate = fail_count / total * 100
avg_health = health_scores.mean()
anomaly_count = int((anomaly_norm > 0.6).sum())
critical_count = int((health_scores < 40).sum())

# ── KPI Row ────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

def kpi_card(col, icon, label, value, color="#00D4FF", delta=None):
    delta_html = f'<div style="font-size:0.72rem;color:#00FF88;margin-top:4px;">{delta}</div>' if delta else ""
    col.markdown(f"""
<div class="metric-card" style="text-align:center;">
  <div style="font-size:1.8rem;">{icon}</div>
  <div class="kpi-label" style="margin:0.3rem 0;">{label}</div>
  <div class="kpi-value" style="color:{color};">{value}</div>
  {delta_html}
</div>""", unsafe_allow_html=True)

kpi_card(c1, "🏭", "Total Machines", f"{total:,}", "#00D4FF")
kpi_card(c2, "⚠️", "Failure Events", f"{fail_count:,}", "#FF4B4B", f"{fail_rate:.1f}% of fleet")
kpi_card(c3, "💚", "Avg Health Score", f"{avg_health:.1f}", "#00FF88")
kpi_card(c4, "🚨", "Anomalies Detected", f"{anomaly_count:,}", "#FF8C00")
kpi_card(c5, "🔴", "Critical Alerts", f"{critical_count:,}", "#FF4B4B")

st.markdown("---")

# ── Health Score Gauge ─────────────────────────────────────────────────────
col_gauge, col_dist = st.columns([1, 2])

with col_gauge:
    st.markdown('<div class="section-title">Fleet Health Gauge</div>', unsafe_allow_html=True)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_health,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Average Health Score", "font": {"color": "#E2E8F0", "size": 14}},
        delta={"reference": 80, "valueformat": ".1f"},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#94A3B8"},
            "bar": {"color": "#00D4FF"},
            "bgcolor": "#1A2236",
            "bordercolor": "rgba(0,212,255,0.3)",
            "steps": [
                {"range": [0, 40], "color": "rgba(255,75,75,0.25)"},
                {"range": [40, 60], "color": "rgba(255,140,0,0.2)"},
                {"range": [60, 80], "color": "rgba(255,215,0,0.15)"},
                {"range": [80, 100], "color": "rgba(0,212,255,0.1)"},
            ],
            "threshold": {
                "line": {"color": "#00FF88", "width": 4},
                "thickness": 0.75,
                "value": 80,
            },
        },
        number={"font": {"color": "#00D4FF", "size": 36}, "suffix": " / 100"},
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E2E8F0",
        height=280,
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_dist:
    st.markdown('<div class="section-title">Health Score Distribution</div>', unsafe_allow_html=True)
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=health_scores,
        nbinsx=30,
        marker=dict(
            color=health_scores,
            colorscale=[[0, "#FF4B4B"], [0.4, "#FF8C00"], [0.6, "#FFD700"], [1.0, "#00D4FF"]],
            showscale=False,
        ),
        opacity=0.85,
    ))
    fig_hist.add_vline(x=avg_health, line_dash="dash", line_color="#00FF88",
                       annotation_text=f"Mean: {avg_health:.1f}", annotation_font_color="#00FF88")
    fig_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(26,34,54,0.5)",
        font_color="#E2E8F0", height=280,
        xaxis_title="Health Score", yaxis_title="Number of Machines",
        margin=dict(t=20, b=40, l=40, r=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ── Recommendation breakdown ───────────────────────────────────────────────
st.markdown('<div class="section-title">Maintenance Status Breakdown</div>', unsafe_allow_html=True)
rec_labels_clean = [l.split(" ", 1)[1] for l in labels]  # remove emoji
from collections import Counter
rec_counts = Counter(rec_labels_clean)

cat_order = ["Immediate Maintenance", "Schedule Maintenance", "Monitor Closely", "Healthy"]
cat_colors = ["#FF4B4B", "#FF8C00", "#FFD700", "#00D4FF"]
cat_vals = [rec_counts.get(c, 0) for c in cat_order]

col_bar, col_pie = st.columns(2)

with col_bar:
    fig_bar = go.Figure(go.Bar(
        x=cat_order, y=cat_vals,
        marker_color=cat_colors,
        text=cat_vals,
        textposition="outside",
        textfont=dict(color="#E2E8F0"),
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(26,34,54,0.5)",
        font_color="#E2E8F0", height=300,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Count"),
        margin=dict(t=20, b=60, l=40, r=20),
        title="Machine Count by Maintenance Category",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_pie:
    fig_pie = go.Figure(go.Pie(
        labels=cat_order, values=cat_vals,
        marker=dict(colors=cat_colors),
        textinfo="label+percent",
        textfont=dict(color="#E2E8F0"),
        hole=0.45,
    ))
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#E2E8F0", height=300,
        legend=dict(font=dict(color="#E2E8F0")),
        margin=dict(t=20, b=20, l=20, r=20),
        title="Fleet Maintenance Distribution",
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Best model banner ──────────────────────────────────────────────────────
best = metrics["best_model"]
bm = metrics["models"][best]
st.markdown("---")
st.markdown(f"""
<div class="metric-card" style="display:flex;gap:2rem;align-items:center;flex-wrap:wrap;">
  <div style="font-size:2rem;">🏆</div>
  <div>
    <div style="font-size:0.75rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.1em;">Best Model</div>
    <div style="font-size:1.4rem;font-weight:800;color:#00D4FF;">{best}</div>
  </div>
  <div style="margin-left:auto;display:flex;gap:2rem;flex-wrap:wrap;">
    <div style="text-align:center;">
      <div style="font-size:0.7rem;color:#94A3B8;">RECALL</div>
      <div style="font-size:1.4rem;font-weight:700;color:#00FF88;">{bm['recall']:.4f}</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:0.7rem;color:#94A3B8;">ROC-AUC</div>
      <div style="font-size:1.4rem;font-weight:700;color:#00FF88;">{bm['roc_auc']:.4f}</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:0.7rem;color:#94A3B8;">F1 SCORE</div>
      <div style="font-size:1.4rem;font-weight:700;color:#00FF88;">{bm['f1']:.4f}</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:0.7rem;color:#94A3B8;">ACCURACY</div>
      <div style="font-size:1.4rem;font-weight:700;color:#00FF88;">{bm['accuracy']:.4f}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Failure mode breakdown ─────────────────────────────────────────────────
st.markdown('<div class="section-title" style="margin-top:1.5rem;">Failure Mode Analysis</div>', unsafe_allow_html=True)
failure_modes = ["TWF", "HDF", "PWF", "OSF", "RNF"]
fm_counts = {m: int(df_feat[m].sum()) for m in failure_modes if m in df_feat.columns}

if fm_counts:
    fig_fm = go.Figure(go.Bar(
        y=list(fm_counts.keys()),
        x=list(fm_counts.values()),
        orientation="h",
        marker=dict(color=["#FF4B4B","#FF8C00","#FFD700","#00D4FF","#9B59B6"]),
        text=list(fm_counts.values()),
        textposition="outside",
        textfont=dict(color="#E2E8F0"),
    ))
    fig_fm.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(26,34,54,0.5)",
        font_color="#E2E8F0", height=250,
        xaxis=dict(title="Count", gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(t=10, b=40, l=60, r=60),
    )
    st.plotly_chart(fig_fm, use_container_width=True)
