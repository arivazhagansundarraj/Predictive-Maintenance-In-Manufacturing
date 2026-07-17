"""
pages/4_Live_Prediction.py
Real-time failure probability prediction with health score gauge and
maintenance recommendation. Includes downloadable CSV report.
"""

import os
import sys
import io
import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.model_training import load_best_model, load_scaler, load_model_metrics
from src.anomaly_detection import load_isolation_forest, predict_anomaly
from src.health_score import compute_health_score
from src.recommendation import get_recommendation
from src.data_processing import FEATURE_COLS

st.set_page_config(page_title="Live Prediction — PredictIQ", page_icon="🔮", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.section-title{font-size:1.3rem;font-weight:700;color:#00D4FF;margin-bottom:0.8rem;}
.metric-card{background:linear-gradient(135deg,#1A2236,#0D1526);border:1px solid rgba(0,212,255,0.15);
  border-radius:16px;padding:1.25rem 1.5rem;margin-bottom:0.5rem;
  box-shadow:0 0 20px rgba(0,212,255,0.15);}
.rec-card{border-radius:16px;padding:1.5rem;margin-top:0.5rem;
  box-shadow:0 0 30px rgba(0,0,0,0.5);}
</style>""", unsafe_allow_html=True)

st.markdown('<h1 class="section-title" style="font-size:2rem;">🔮 Live Prediction Interface</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#94A3B8;margin-top:-0.5rem;">Enter real-time sensor readings to get instant failure probability and maintenance recommendations</p>', unsafe_allow_html=True)

@st.cache_resource
def load_models():
    return load_best_model(), load_scaler(), load_isolation_forest()

model, scaler, iso = load_models()
metrics_data = load_model_metrics()
best_name = metrics_data["best_model"]

# ── Helper: build gauge ────────────────────────────────────────────────────
def make_gauge(value, title, color, suffix="", max_val=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": title, "font": {"color": "#E2E8F0", "size": 13}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#94A3B8"},
            "bar": {"color": color},
            "bgcolor": "#1A2236",
            "bordercolor": "rgba(0,212,255,0.2)",
            "steps": [
                {"range": [0, max_val * 0.33], "color": "rgba(0,212,255,0.08)"},
                {"range": [max_val * 0.33, max_val * 0.66], "color": "rgba(255,184,0,0.08)"},
                {"range": [max_val * 0.66, max_val], "color": "rgba(255,75,75,0.08)"},
            ],
        },
        number={"font": {"color": color, "size": 34}, "suffix": suffix},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_color="#E2E8F0",
        height=220, margin=dict(t=40, b=10, l=20, r=20),
    )
    return fig

# ── Sidebar: sensor inputs ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Machine Inputs")
    product_type = st.selectbox("Product Type", ["L (Low)", "M (Medium)", "H (High)"], index=1)
    type_val = {"L (Low)": 0, "M (Medium)": 1, "H (High)": 2}[product_type]

    air_temp = st.slider("Air Temperature (K)", 295.0, 305.0, 300.0, 0.1)
    proc_temp = st.slider("Process Temperature (K)", 306.0, 314.0, 310.0, 0.1)
    rot_speed = st.slider("Rotational Speed (rpm)", 1168, 2886, 1500, 1)
    torque = st.slider("Torque (Nm)", 3.8, 76.6, 40.0, 0.1)
    tool_wear = st.slider("Tool Wear (min)", 0, 253, 100, 1)

    st.markdown("---")
    machine_id = st.text_input("Machine ID (optional)", value="MACH-001")

# ── Compute engineered features ────────────────────────────────────────────
temp_diff = proc_temp - air_temp
wear_rate = tool_wear / (rot_speed + 1e-6)
mech_load = torque * tool_wear / 1000.0

raw_features = np.array([[type_val, air_temp, proc_temp, rot_speed, torque, tool_wear,
                           temp_diff, wear_rate, mech_load]])
X_scaled = scaler.transform(raw_features)

failure_prob = float(model.predict_proba(X_scaled)[0, 1])
_, _, anomaly_norm = predict_anomaly(iso, X_scaled)
anomaly_score = float(anomaly_norm[0])

row_dict = {
    "Air temperature [K]": air_temp,
    "Process temperature [K]": proc_temp,
    "Rotational speed [rpm]": rot_speed,
    "Torque [Nm]": torque,
    "Tool wear [min]": tool_wear,
    "Temperature Difference": temp_diff,
    "Wear Rate": wear_rate,
    "Mechanical Load Index": mech_load,
}
health = compute_health_score(failure_prob, anomaly_score, row_dict)
rec = get_recommendation(health)

# ── Main layout ────────────────────────────────────────────────────────────
col_l, col_r = st.columns([3, 2])

with col_l:
    st.markdown('<div class="section-title">Engineered Features</div>', unsafe_allow_html=True)
    ef_c1, ef_c2, ef_c3 = st.columns(3)
    for col, label, val, fmt, color in [
        (ef_c1, "Temperature Difference", temp_diff, ".2f K", "#FF8C00"),
        (ef_c2, "Wear Rate", wear_rate * 1000, ".4f ×10⁻³", "#FF4B4B"),
        (ef_c3, "Mechanical Load Index", mech_load, ".3f", "#FFD700"),
    ]:
        col.markdown(f"""
<div class="metric-card" style="text-align:center;">
  <div style="font-size:0.7rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.1em;">{label}</div>
  <div style="font-size:1.6rem;font-weight:800;color:{color};">{val:{fmt.split()[0]}}</div>
  <div style="font-size:0.7rem;color:#64748B;">{fmt.split()[-1] if len(fmt.split()) > 1 else ''}</div>
</div>""", unsafe_allow_html=True)

    # Gauges row
    g1, g2, g3 = st.columns(3)
    with g1:
        prob_color = "#FF4B4B" if failure_prob > 0.5 else "#FFD700" if failure_prob > 0.25 else "#00D4FF"
        st.plotly_chart(make_gauge(failure_prob * 100, "Failure Probability", prob_color, "%"), use_container_width=True)
    with g2:
        anom_color = "#FF4B4B" if anomaly_score > 0.6 else "#FFD700" if anomaly_score > 0.4 else "#00D4FF"
        st.plotly_chart(make_gauge(anomaly_score * 100, "Anomaly Score", anom_color, "%"), use_container_width=True)
    with g3:
        health_color = "#FF4B4B" if health < 40 else "#FF8C00" if health < 60 else "#FFD700" if health < 80 else "#00FF88"
        st.plotly_chart(make_gauge(health, "Machine Health", health_color, " / 100"), use_container_width=True)

    # Feature radar
    st.markdown('<div class="section-title" style="margin-top:0.5rem;">Input Sensor Radar</div>', unsafe_allow_html=True)
    sensor_labels = ["Air Temp (K)", "Proc Temp (K)", "Rot Speed (rpm)", "Torque (Nm)", "Tool Wear (min)"]
    sensor_raw = [air_temp, proc_temp, rot_speed, torque, tool_wear]
    sensor_norm = [
        (air_temp - 295) / 10,
        (proc_temp - 306) / 8,
        (rot_speed - 1168) / 1718,
        (torque - 3.8) / 72.8,
        tool_wear / 253,
    ]
    sensor_norm_closed = sensor_norm + [sensor_norm[0]]
    labels_closed = sensor_labels + [sensor_labels[0]]

    fig_radar = go.Figure(go.Scatterpolar(
        r=sensor_norm_closed, theta=labels_closed,
        fill="toself",
        fillcolor="rgba(0,212,255,0.15)",
        line=dict(color="#00D4FF", width=2),
        name="Current Readings",
    ))
    fig_radar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_color="#E2E8F0", height=300,
        polar=dict(
            bgcolor="rgba(26,34,54,0.5)",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        ),
        margin=dict(t=20, b=20, l=20, r=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_r:
    st.markdown('<div class="section-title">Maintenance Recommendation</div>', unsafe_allow_html=True)

    border_color = rec["color"]
    st.markdown(f"""
<div class="rec-card" style="background:linear-gradient(135deg,rgba(26,34,54,0.9),rgba(13,21,38,0.9));
  border:2px solid {border_color}; box-shadow: 0 0 30px {border_color}40;">
  <div style="font-size:2rem;margin-bottom:0.5rem;">{rec['emoji']}</div>
  <div style="font-size:1.4rem;font-weight:800;color:{border_color};">{rec['name']}</div>
  <div style="display:inline-block;background:rgba(255,255,255,0.1);border:1px solid {border_color};
    border-radius:999px;padding:0.15rem 0.75rem;font-size:0.7rem;font-weight:700;color:{border_color};margin:0.4rem 0;">
    Priority: {rec['priority']}
  </div>
  <div style="font-size:0.85rem;color:#94A3B8;margin-top:0.5rem;line-height:1.5;">{rec['description']}</div>
  <hr style="border-color:rgba(255,255,255,0.1);margin:1rem 0;">
  <div style="font-size:0.8rem;font-weight:700;color:#E2E8F0;margin-bottom:0.5rem;">Recommended Actions:</div>
  {''.join(f'<div style="display:flex;gap:0.5rem;align-items:flex-start;margin-bottom:0.4rem;"><span style="color:{border_color};font-size:0.8rem;">▸</span><span style="font-size:0.8rem;color:#CBD5E1;">{a}</span></div>' for a in rec['actions'])}
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:1.5rem;">Summary Metrics</div>', unsafe_allow_html=True)
    for label, val, color in [
        ("Failure Probability", f"{failure_prob*100:.1f}%", prob_color),
        ("Anomaly Score", f"{anomaly_score*100:.1f}%", anom_color),
        ("Health Score", f"{health:.1f} / 100", health_color),
        ("Model Used", best_name, "#00D4FF"),
    ]:
        st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
  padding:0.4rem 0;border-bottom:1px solid rgba(255,255,255,0.05);">
  <span style="font-size:0.8rem;color:#94A3B8;">{label}</span>
  <span style="font-size:0.9rem;font-weight:700;color:{color};">{val}</span>
</div>""", unsafe_allow_html=True)

# ── Download report ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-title">📥 Download Prediction Report</div>', unsafe_allow_html=True)

report_data = {
    "Timestamp": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    "Machine ID": [machine_id],
    "Product Type": [product_type],
    "Air Temperature (K)": [air_temp],
    "Process Temperature (K)": [proc_temp],
    "Rotational Speed (rpm)": [rot_speed],
    "Torque (Nm)": [torque],
    "Tool Wear (min)": [tool_wear],
    "Temperature Difference": [round(temp_diff, 4)],
    "Wear Rate": [round(wear_rate, 6)],
    "Mechanical Load Index": [round(mech_load, 4)],
    "Failure Probability (%)": [round(failure_prob * 100, 2)],
    "Anomaly Score (%)": [round(anomaly_score * 100, 2)],
    "Health Score": [round(health, 2)],
    "Recommendation": [rec["name"]],
    "Priority": [rec["priority"]],
    "Model": [best_name],
}
df_report = pd.DataFrame(report_data)

csv_buf = io.StringIO()
df_report.to_csv(csv_buf, index=False)

st.download_button(
    label="⬇️ Download CSV Report",
    data=csv_buf.getvalue().encode("utf-8"),
    file_name=f"prediction_report_{machine_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
)
st.dataframe(df_report.T.rename(columns={0: "Value"}), use_container_width=True)
