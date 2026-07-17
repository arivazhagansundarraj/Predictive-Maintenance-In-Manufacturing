"""
app.py
Main entry point for the Predictive Maintenance Streamlit application.
Bootstraps model training on first run, then serves the multi-page app.
"""

import os
import sys
import streamlit as st

# ── ensure src/ is importable ──────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="PredictIQ — Smart Maintenance",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── global CSS ─────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Import fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root variables ── */
:root {
    --bg-primary:   #0A0E1A;
    --bg-secondary: #111827;
    --bg-card:      #1A2236;
    --accent-cyan:  #00D4FF;
    --accent-green: #00FF88;
    --accent-amber: #FFB800;
    --accent-red:   #FF4B4B;
    --text-primary: #E2E8F0;
    --text-muted:   #94A3B8;
    --border:       rgba(0,212,255,0.15);
    --glow:         0 0 20px rgba(0,212,255,0.3);
}

/* ── Global typography ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1526 0%, #111827 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1rem !important;
}

/* ── Cards ── */
.metric-card {
    background: linear-gradient(135deg, #1A2236 0%, #0D1526 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--glow);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 30px rgba(0,212,255,0.4);
}
.metric-card h3 {
    color: var(--text-muted);
    font-size: 0.8rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0 0 0.4rem 0;
}
.metric-card .metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--accent-cyan);
    line-height: 1;
}
.metric-card .metric-delta {
    font-size: 0.75rem;
    color: var(--accent-green);
    margin-top: 0.25rem;
}

/* ── Section headers ── */
.section-header {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--accent-cyan);
    border-bottom: 2px solid var(--border);
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
}

/* ── Status badges ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.badge-critical { background: rgba(255,75,75,0.2); color: #FF4B4B; border: 1px solid #FF4B4B; }
.badge-high     { background: rgba(255,140,0,0.2); color: #FF8C00; border: 1px solid #FF8C00; }
.badge-medium   { background: rgba(255,215,0,0.2); color: #FFD700; border: 1px solid #FFD700; }
.badge-low      { background: rgba(0,212,255,0.2); color: #00D4FF; border: 1px solid #00D4FF; }

/* ── Streamlit tweaks ── */
.stButton > button {
    background: linear-gradient(135deg, #00D4FF, #0099BB) !important;
    color: #0A0E1A !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent-cyan) !important;
    border-bottom-color: var(--accent-cyan) !important;
}

div[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    color: var(--accent-cyan) !important;
}
div[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ── Plotly chart backgrounds ── */
.js-plotly-plot .plotly .modebar {
    background: transparent !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Model bootstrap ────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def bootstrap_models():
    from src.model_training import train_all_models, models_exist
    from src.data_processing import run_pipeline
    from src.anomaly_detection import train_isolation_forest, iso_model_exists

    if not models_exist():
        with st.spinner("🔧 First-time setup: training AI models (60–90 sec)..."):
            pipeline_data = run_pipeline()
            train_all_models(pipeline_data)

            # Isolation Forest: train on normal samples from full feature set
            import numpy as np
            from src.data_processing import FEATURE_COLS, TARGET_COL
            df_feat = pipeline_data["df_feat"]
            normal_mask = df_feat[TARGET_COL] == 0
            from sklearn.preprocessing import StandardScaler
            from src.model_training import load_scaler
            scaler = load_scaler()
            X_normal = scaler.transform(df_feat.loc[normal_mask, FEATURE_COLS].values)
            train_isolation_forest(X_normal)

    return True


ready = bootstrap_models()

# ── Sidebar branding ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
<div style="text-align:center; padding: 1rem 0 1.5rem 0;">
  <div style="font-size:2.5rem;">⚙️</div>
  <div style="font-size:1.3rem; font-weight:800; color:#00D4FF; letter-spacing:0.05em;">PredictIQ</div>
  <div style="font-size:0.75rem; color:#94A3B8; margin-top:0.2rem;">Smart Manufacturing AI</div>
  <hr style="border-color:rgba(0,212,255,0.2); margin: 1rem 0 0.5rem 0;">
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
**Navigation**

Use the page list below to explore all modules.

---
<div style="font-size:0.7rem; color:#64748B; margin-top:1rem;">
Dataset: AI4I 2020 Predictive Maintenance<br>
Models: RF · XGBoost · LightGBM · CatBoost<br>
Anomaly: Isolation Forest
</div>
""",
        unsafe_allow_html=True,
    )

# ── Home landing ───────────────────────────────────────────────────────────
st.markdown(
    """
<div style="text-align:center; padding: 3rem 0 2rem 0;">
  <div style="font-size:4rem; margin-bottom:0.5rem;">⚙️</div>
  <h1 style="font-size:2.8rem; font-weight:800; color:#00D4FF; margin:0;">PredictIQ</h1>
  <p style="font-size:1.1rem; color:#94A3B8; margin-top:0.5rem;">
    Industrial IoT Predictive Maintenance Platform
  </p>
  <div style="display:flex; gap:0.5rem; justify-content:center; margin-top:1rem; flex-wrap:wrap;">
    <span class="badge badge-low">AI-Powered</span>
    <span class="badge badge-low">Real-Time Monitoring</span>
    <span class="badge badge-low">4 ML Models</span>
    <span class="badge badge-low">Anomaly Detection</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

pages_info = [
    ("🏠", "Home Dashboard",  "KPIs, gauges & live overview",           "pages/1_Home_Dashboard.py"),
    ("📊", "Dataset Insights", "EDA, distributions & SMOTE",             "pages/2_Dataset_Insights.py"),
    ("🏆", "Model Evaluation", "Metrics, ROC curves & feature importance","pages/3_Model_Evaluation.py"),
    ("🔮", "Live Prediction",  "Real-time failure probability",           "pages/4_Live_Prediction.py"),
    ("🚨", "Anomaly Detection","Isolation Forest dashboard",              "pages/5_Anomaly_Detection.py"),
    ("🔧", "Maintenance Panel","Recommendations & batch reports",         "pages/6_Maintenance_Recommendations.py"),
]

# Extra CSS: make the Streamlit button fill its card and look invisible
st.markdown(
    """
<style>
/* Make nav buttons fill the card and appear seamless */
.nav-card-wrapper { position: relative; }
.nav-card-wrapper .stButton { position: absolute; inset: 0; z-index: 10; }
.nav-card-wrapper .stButton > button {
    width: 100% !important;
    height: 100% !important;
    background: transparent !important;
    color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    cursor: pointer !important;
    padding: 0 !important;
    border-radius: 16px !important;
}
.nav-card-wrapper .stButton > button:hover {
    background: rgba(0,212,255,0.08) !important;
    opacity: 1 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

cols = st.columns(3)
for i, (icon, title, desc, page_path) in enumerate(pages_info):
    with cols[i % 3]:
        st.markdown(
            f"""
<div class="nav-card-wrapper">
  <div class="metric-card" style="text-align:center; cursor:pointer;">
    <div style="font-size:2rem;">{icon}</div>
    <div style="font-weight:700; color:#E2E8F0; margin:0.4rem 0 0.2rem;">{title}</div>
    <div style="font-size:0.8rem; color:#94A3B8;">{desc}</div>
  </div>
""",
            unsafe_allow_html=True,
        )
        if st.button(title, key=f"nav_{i}"):
            st.switch_page(page_path)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
<div style="text-align:center; margin-top:2rem; color:#64748B; font-size:0.8rem;">
  ← Use the sidebar to navigate between modules
</div>
""",
    unsafe_allow_html=True,
)
