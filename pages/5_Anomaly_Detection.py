"""
pages/5_Anomaly_Detection.py
Isolation Forest anomaly dashboard with scatter plots and alert table.
Supports both slider-based single prediction and CSV batch upload.
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
from src.model_training import load_scaler
from src.anomaly_detection import load_isolation_forest, predict_anomaly

st.set_page_config(page_title="Anomaly Detection — PredictIQ", page_icon="🚨", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.section-title{font-size:1.3rem;font-weight:700;color:#00D4FF;margin-bottom:0.8rem;}
.metric-card{background:linear-gradient(135deg,#1A2236,#0D1526);border:1px solid rgba(0,212,255,0.15);
  border-radius:16px;padding:1.25rem 1.5rem;margin-bottom:0.5rem;}
.alert-row{padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.05);}
</style>""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(26,34,54,0.5)",
    font_color="#E2E8F0",
)

st.markdown('<h1 class="section-title" style="font-size:2rem;">🚨 Anomaly Detection Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#94A3B8;margin-top:-0.5rem;">Isolation Forest-based anomaly detection across manufacturing sensors</p>', unsafe_allow_html=True)

@st.cache_resource
def load_models_and_data():
    scaler = load_scaler()
    iso = load_isolation_forest()
    df_raw = load_raw_data()
    df_clean = clean_data(df_raw)
    df_feat = engineer_features(df_clean)
    return scaler, iso, df_feat

scaler, iso, df_feat = load_models_and_data()

# ── Mode selector ──────────────────────────────────────────────────────────
mode = st.radio("Analysis Mode", ["📊 Full Dataset Analysis", "📁 Upload CSV", "🎛️ Single Observation"],
                horizontal=True)
st.markdown("---")

# ── Helper ─────────────────────────────────────────────────────────────────
def run_anomaly(df_to_score: pd.DataFrame):
    """Score a dataframe; returns df with anomaly columns."""
    X = scaler.transform(df_to_score[FEATURE_COLS].values)
    scores_raw, labels, norm_scores = predict_anomaly(iso, X)
    result = df_to_score.copy()
    result["Anomaly Score (norm)"] = np.round(norm_scores * 100, 2)
    result["Anomaly Label"] = np.where(labels == -1, "⚠️ Anomaly", "✅ Normal")
    result["Raw IF Score"] = np.round(scores_raw, 5)
    return result, norm_scores, labels


def anomaly_charts(df_res, norm_scores, labels, title_suffix=""):
    # KPI
    n_total = len(df_res)
    n_anom = int((labels == -1).sum())
    c1, c2, c3 = st.columns(3)
    for col, lbl, val, color in [
        (c1, "Total Observations", f"{n_total:,}", "#00D4FF"),
        (c2, "Anomalies Detected", f"{n_anom:,}", "#FF4B4B"),
        (c3, "Anomaly Rate", f"{n_anom/n_total*100:.2f}%", "#FF8C00"),
    ]:
        col.markdown(f"""
<div class="metric-card" style="text-align:center;">
  <div style="font-size:0.75rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.1em;">{lbl}</div>
  <div style="font-size:2rem;font-weight:800;color:{color};">{val}</div>
</div>""", unsafe_allow_html=True)

    # Score histogram
    st.markdown(f'<div class="section-title">Anomaly Score Distribution {title_suffix}</div>', unsafe_allow_html=True)
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=norm_scores[labels == 1] * 100, name="Normal",
        marker_color="#00D4FF", opacity=0.75, nbinsx=40,
    ))
    fig_hist.add_trace(go.Histogram(
        x=norm_scores[labels == -1] * 100, name="Anomaly",
        marker_color="#FF4B4B", opacity=0.85, nbinsx=40,
    ))
    fig_hist.add_vline(x=60, line_dash="dash", line_color="#FFD700",
                       annotation_text="Alert threshold (60)", annotation_font_color="#FFD700")
    fig_hist.update_layout(
        **PLOTLY_LAYOUT, height=320, barmode="overlay",
        xaxis_title="Anomaly Score (%)", yaxis_title="Count",
        legend=dict(font=dict(color="#E2E8F0"), bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # 2D scatter
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown('<div class="section-title">Torque vs Rotational Speed</div>', unsafe_allow_html=True)
        sample_idx = np.random.choice(len(df_res), min(2000, len(df_res)), replace=False)
        df_sample = df_res.iloc[sample_idx]
        fig_sc = px.scatter(
            df_sample,
            x="Rotational speed [rpm]" if "Rotational speed [rpm]" in df_sample.columns else df_sample.columns[3],
            y="Torque [Nm]" if "Torque [Nm]" in df_sample.columns else df_sample.columns[4],
            color="Anomaly Label",
            color_discrete_map={"⚠️ Anomaly": "#FF4B4B", "✅ Normal": "#00D4FF"},
            size="Anomaly Score (norm)",
            size_max=12,
            opacity=0.7,
        )
        fig_sc.update_layout(**PLOTLY_LAYOUT, height=350,
                             legend=dict(font=dict(color="#E2E8F0"), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_sc, use_container_width=True)

    with col_s2:
        st.markdown('<div class="section-title">Temperature vs Tool Wear</div>', unsafe_allow_html=True)
        fig_sc2 = px.scatter(
            df_sample,
            x="Tool wear [min]" if "Tool wear [min]" in df_sample.columns else df_sample.columns[5],
            y="Air temperature [K]" if "Air temperature [K]" in df_sample.columns else df_sample.columns[1],
            color="Anomaly Label",
            color_discrete_map={"⚠️ Anomaly": "#FF4B4B", "✅ Normal": "#00D4FF"},
            size="Anomaly Score (norm)",
            size_max=12,
            opacity=0.7,
        )
        fig_sc2.update_layout(**PLOTLY_LAYOUT, height=350,
                              legend=dict(font=dict(color="#E2E8F0"), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_sc2, use_container_width=True)

    # Alert table
    st.markdown('<div class="section-title">⚠️ Anomaly Alert Table</div>', unsafe_allow_html=True)
    anomalies = df_res[df_res["Anomaly Label"] == "⚠️ Anomaly"].sort_values(
        "Anomaly Score (norm)", ascending=False
    )
    if len(anomalies) > 0:
        display_cols = [c for c in FEATURE_COLS if c in anomalies.columns] + \
                       ["Anomaly Score (norm)", "Anomaly Label"]
        st.dataframe(anomalies[display_cols].head(100), use_container_width=True, height=300)

        # Download anomaly report
        csv_buf = io.StringIO()
        anomalies[display_cols].to_csv(csv_buf, index=False)
        st.download_button(
            "⬇️ Download Anomaly Report (CSV)",
            data=csv_buf.getvalue().encode("utf-8"),
            file_name=f"anomaly_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.success("No anomalies detected in this dataset!")


# ── Mode: Full Dataset ─────────────────────────────────────────────────────
if mode == "📊 Full Dataset Analysis":
    with st.spinner("Scoring all 10,000 records..."):
        df_res, norm_scores, labels = run_anomaly(df_feat)
    anomaly_charts(df_res, norm_scores, labels, "(Full Dataset)")

# ── Mode: Upload CSV ───────────────────────────────────────────────────────
elif mode == "📁 Upload CSV":
    st.markdown("Upload a CSV with the same columns as the AI4I dataset (or a subset of sensor columns).")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        df_up = pd.read_csv(uploaded)
        st.dataframe(df_up.head(), use_container_width=True)
        try:
            df_up_clean = clean_data(df_up)
            df_up_feat = engineer_features(df_up_clean)
            df_res, norm_scores, labels = run_anomaly(df_up_feat)
            anomaly_charts(df_res, norm_scores, labels, "(Uploaded Data)")
        except Exception as e:
            st.error(f"Could not process file: {e}. Make sure it contains the required sensor columns.")
    else:
        st.info("Please upload a CSV file to begin anomaly analysis.")

# ── Mode: Single Observation ───────────────────────────────────────────────
elif mode == "🎛️ Single Observation":
    col_in, col_out = st.columns(2)
    with col_in:
        st.markdown('<div class="section-title">Sensor Inputs</div>', unsafe_allow_html=True)
        s_type = st.selectbox("Product Type", ["L", "M", "H"], index=1)
        s_air = st.slider("Air Temp (K)", 295.0, 305.0, 300.0, 0.1)
        s_proc = st.slider("Process Temp (K)", 306.0, 314.0, 310.0, 0.1)
        s_rot = st.slider("Rotational Speed (rpm)", 1168, 2886, 1500)
        s_torq = st.slider("Torque (Nm)", 3.8, 76.6, 40.0, 0.1)
        s_wear = st.slider("Tool Wear (min)", 0, 253, 100)

    type_map = {"L": 0, "M": 1, "H": 2}
    temp_diff = s_proc - s_air
    wear_rate = s_wear / (s_rot + 1e-6)
    mech_load = s_torq * s_wear / 1000.0
    raw = np.array([[type_map[s_type], s_air, s_proc, s_rot, s_torq, s_wear,
                     temp_diff, wear_rate, mech_load]])
    X_sc = scaler.transform(raw)

    # Get raw IF score and label directly from the model (bypasses any cached normalize logic)
    scores_raw = iso.score_samples(X_sc)   # shape (1,) — more negative = more anomalous
    lbl        = iso.predict(X_sc)         # 1=normal, -1=anomaly

    # Map IF score → 0–100%:  -0.10 → 0% (very normal),  -0.70 → 100% (very anomalous)
    _NORM  = -0.10   # typical upper bound (normal region)
    _ANOM  = -0.70   # typical lower bound (anomaly region)
    raw_score = float(scores_raw[0])
    anom_pct  = max(0.0, min(100.0, (_NORM - raw_score) / (_NORM - _ANOM) * 100))
    is_anomaly = int(lbl[0]) == -1

    with col_out:
        st.markdown('<div class="section-title">Anomaly Result</div>', unsafe_allow_html=True)
        color = "#FF4B4B" if is_anomaly else "#00D4FF"
        emoji = "⚠️" if is_anomaly else "✅"
        label = "ANOMALY DETECTED" if is_anomaly else "NORMAL OPERATION"
        st.markdown(f"""
<div class="metric-card" style="border-color:{color};box-shadow:0 0 30px {color}40;text-align:center;">
  <div style="font-size:3rem;">{emoji}</div>
  <div style="font-size:1.4rem;font-weight:800;color:{color};margin:0.5rem 0;">{label}</div>
  <div style="font-size:2.5rem;font-weight:800;color:{color};">{anom_pct:.1f}%</div>
  <div style="font-size:0.8rem;color:#94A3B8;">Anomaly Score</div>
  <div style="margin-top:0.75rem;font-size:0.8rem;color:#94A3B8;">Raw IF Score: {raw_score:.5f}</div>
</div>""", unsafe_allow_html=True)

        # Score bar chart
        fig_bar = go.Figure(go.Bar(
            x=["Normal Zone", "Warning Zone", "Anomaly Zone", "This Observation"],
            y=[40, 20, 40, anom_pct],
            marker_color=[
                "rgba(0,212,255,0.3)",    # Normal Zone — dim
                "rgba(255,215,0,0.3)",    # Warning Zone — dim
                "rgba(255,75,75,0.3)",    # Anomaly Zone — dim
                color,                    # This Observation — full color
            ],
        ))
        fig_bar.update_layout(**PLOTLY_LAYOUT, height=250, showlegend=False,
                              yaxis=dict(title="Score (%)", gridcolor="rgba(255,255,255,0.05)"),
                              xaxis=dict(gridcolor="rgba(255,255,255,0.05)"))
        st.plotly_chart(fig_bar, use_container_width=True)
