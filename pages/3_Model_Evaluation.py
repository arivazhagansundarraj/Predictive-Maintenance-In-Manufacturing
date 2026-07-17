"""
pages/3_Model_Evaluation.py
Side-by-side model comparison, ROC curves, confusion matrices, feature importance.
"""

import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.model_training import load_model_metrics, load_best_model
from src.feature_importance import get_importance_df
from src.data_processing import FEATURE_COLS

st.set_page_config(page_title="Model Evaluation — PredictIQ", page_icon="🏆", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.section-title{font-size:1.3rem;font-weight:700;color:#00D4FF;margin-bottom:0.8rem;}
.metric-card{background:linear-gradient(135deg,#1A2236,#0D1526);border:1px solid rgba(0,212,255,0.15);
  border-radius:16px;padding:1rem 1.5rem;margin-bottom:0.5rem;}
.best-badge{background:rgba(0,255,136,0.15);border:1px solid #00FF88;
  border-radius:999px;padding:0.15rem 0.6rem;font-size:0.7rem;color:#00FF88;font-weight:700;}
</style>""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(26,34,54,0.5)",
    font_color="#E2E8F0",
)

st.markdown('<h1 class="section-title" style="font-size:2rem;">🏆 Model Evaluation</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#94A3B8;margin-top:-0.5rem;">Comparative analysis of all trained classifiers with full diagnostic charts</p>', unsafe_allow_html=True)

@st.cache_data
def get_metrics():
    return load_model_metrics()

metrics = get_metrics()
best_name = metrics["best_model"]
models_data = metrics["models"]
model_names = list(models_data.keys())
colors = ["#00D4FF", "#FF8C00", "#00FF88", "#9B59B6"]
model_colors = {n: c for n, c in zip(model_names, colors)}

# ── Metrics Table ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Performance Comparison</div>', unsafe_allow_html=True)

rows = []
for name, m in models_data.items():
    rows.append({
        "Model": f"{'⭐ ' if name == best_name else ''}{name}",
        "Accuracy": f"{m['accuracy']:.4f}",
        "Precision": f"{m['precision']:.4f}",
        "Recall ↑": f"{m['recall']:.4f}",
        "F1 Score": f"{m['f1']:.4f}",
        "ROC-AUC ↑": f"{m['roc_auc']:.4f}",
    })
df_table = pd.DataFrame(rows)

def highlight_best(s):
    return ["background-color: rgba(0,255,136,0.1); color: #00FF88; font-weight: bold;"
            if "⭐" in str(s["Model"]) else "" for _ in s]

st.dataframe(
    df_table.style.apply(highlight_best, axis=1),
    use_container_width=True, hide_index=True,
)

st.info(f"**Best Model:** {best_name} — selected by harmonic mean of Recall and ROC-AUC (maximises failure detection sensitivity).")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Bar Comparison", "📉 ROC & PR Curves", "🔲 Confusion Matrix", "🌟 Feature Importance"])

with tab1:
    metric_keys = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]
    fig_bar = go.Figure()
    for name, m in models_data.items():
        fig_bar.add_trace(go.Bar(
            name=name,
            x=metric_labels,
            y=[m[k] for k in metric_keys],
            marker_color=model_colors[name],
            text=[f"{m[k]:.3f}" for k in metric_keys],
            textposition="outside",
            textfont=dict(color="#E2E8F0", size=10),
        ))
    fig_bar.update_layout(
        **PLOTLY_LAYOUT, height=420, barmode="group",
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(range=[0, 1.15], gridcolor="rgba(255,255,255,0.05)", title="Score"),
        legend=dict(font=dict(color="#E2E8F0"), bgcolor="rgba(0,0,0,0)"),
        title="All Metrics — All Models",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Radar chart
    fig_radar = go.Figure()
    for name, m in models_data.items():
        vals = [m[k] for k in metric_keys] + [m[metric_keys[0]]]
        cats = metric_labels + [metric_labels[0]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals, theta=cats, name=name,
            line=dict(color=model_colors[name], width=2),
            fill="toself",
            fillcolor=model_colors[name].replace(")", ",0.1)").replace("rgb", "rgba") if "rgb" in model_colors[name] else model_colors[name],
        ))
    fig_radar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_color="#E2E8F0", height=400,
        polar=dict(
            bgcolor="rgba(26,34,54,0.5)",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        ),
        legend=dict(font=dict(color="#E2E8F0"), bgcolor="rgba(0,0,0,0)"),
        title="Radar Chart — Model Performance",
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with tab2:
    col_roc, col_pr = st.columns(2)
    with col_roc:
        st.markdown('<div class="section-title">ROC Curves</div>', unsafe_allow_html=True)
        fig_roc = go.Figure()
        fig_roc.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1], mode="lines",
            line=dict(dash="dash", color="#64748B", width=1),
            name="Random Classifier",
        ))
        for name, m in models_data.items():
            fig_roc.add_trace(go.Scatter(
                x=m["roc_fpr"], y=m["roc_tpr"],
                mode="lines", name=f"{name} (AUC={m['roc_auc']:.3f})",
                line=dict(color=model_colors[name], width=2 + (1 if name == best_name else 0)),
            ))
        fig_roc.update_layout(
            **PLOTLY_LAYOUT, height=400,
            xaxis=dict(title="False Positive Rate", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="True Positive Rate", gridcolor="rgba(255,255,255,0.05)"),
            legend=dict(font=dict(color="#E2E8F0", size=10), bgcolor="rgba(0,0,0,0)"),
            title="ROC Curves — All Models",
        )
        st.plotly_chart(fig_roc, use_container_width=True)

    with col_pr:
        st.markdown('<div class="section-title">Precision-Recall Curves</div>', unsafe_allow_html=True)
        fig_pr = go.Figure()
        for name, m in models_data.items():
            fig_pr.add_trace(go.Scatter(
                x=m["pr_recall"], y=m["pr_precision"],
                mode="lines", name=name,
                line=dict(color=model_colors[name], width=2),
            ))
        fig_pr.update_layout(
            **PLOTLY_LAYOUT, height=400,
            xaxis=dict(title="Recall", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="Precision", gridcolor="rgba(255,255,255,0.05)"),
            legend=dict(font=dict(color="#E2E8F0", size=10), bgcolor="rgba(0,0,0,0)"),
            title="Precision-Recall Curves",
        )
        st.plotly_chart(fig_pr, use_container_width=True)

with tab3:
    st.markdown('<div class="section-title">Confusion Matrices</div>', unsafe_allow_html=True)
    cols_cm = st.columns(2)
    for idx, (name, m) in enumerate(models_data.items()):
        with cols_cm[idx % 2]:
            cm = np.array(m["confusion_matrix"])
            labels_cm = ["Normal (0)", "Failure (1)"]
            fig_cm = go.Figure(go.Heatmap(
                z=cm, x=labels_cm, y=labels_cm,
                colorscale=[[0, "#0A0E1A"], [1, "#00D4FF"]],
                text=cm, texttemplate="%{text}",
                textfont=dict(size=18, color="#E2E8F0"),
                colorbar=dict(tickcolor="#E2E8F0"),
            ))
            fig_cm.update_layout(
                **PLOTLY_LAYOUT, height=300,
                title=f"{'⭐ ' if name == best_name else ''}{name}",
                xaxis=dict(title="Predicted", gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(title="Actual", gridcolor="rgba(255,255,255,0.05)"),
                margin=dict(t=50, b=50, l=80, r=30),
            )
            st.plotly_chart(fig_cm, use_container_width=True)

            tn, fp, fn, tp = cm.ravel()
            st.markdown(f"""
<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem;">
  <div style="text-align:center;flex:1;"><div style="font-size:0.65rem;color:#94A3B8;">TRUE NEG</div><div style="font-weight:700;color:#00D4FF;">{tn}</div></div>
  <div style="text-align:center;flex:1;"><div style="font-size:0.65rem;color:#94A3B8;">FALSE POS</div><div style="font-weight:700;color:#FF8C00;">{fp}</div></div>
  <div style="text-align:center;flex:1;"><div style="font-size:0.65rem;color:#94A3B8;">FALSE NEG</div><div style="font-weight:700;color:#FF4B4B;">{fn}</div></div>
  <div style="text-align:center;flex:1;"><div style="font-size:0.65rem;color:#94A3B8;">TRUE POS</div><div style="font-weight:700;color:#00FF88;">{tp}</div></div>
</div>""", unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section-title">Feature Importance — Best Model</div>', unsafe_allow_html=True)
    try:
        best_model = load_best_model()
        imp_df = get_importance_df(best_model, FEATURE_COLS)

        fig_imp = go.Figure(go.Bar(
            y=imp_df["Feature"],
            x=imp_df["Importance %"],
            orientation="h",
            marker=dict(
                color=imp_df["Importance %"],
                colorscale=[[0, "#1A2236"], [0.5, "#00D4FF"], [1, "#00FF88"]],
                showscale=False,
            ),
            text=[f"{v:.1f}%" for v in imp_df["Importance %"]],
            textposition="outside",
            textfont=dict(color="#E2E8F0"),
        ))
        fig_imp.update_layout(
            **PLOTLY_LAYOUT, height=420,
            yaxis=dict(autorange="reversed", gridcolor="rgba(255,255,255,0.05)"),
            xaxis=dict(title="Importance (%)", gridcolor="rgba(255,255,255,0.05)"),
            title=f"Feature Importances — {best_name}",
        )  # xaxis/yaxis safe: not in PLOTLY_LAYOUT
        st.plotly_chart(fig_imp, use_container_width=True)
        st.dataframe(imp_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning(f"Feature importance not available: {e}")

    # Cross-model feature importance comparison
    st.markdown('<div class="section-title" style="margin-top:1rem;">Feature Importances — All Models</div>', unsafe_allow_html=True)
    fig_all_imp = go.Figure()
    for name, m in models_data.items():
        fi = m.get("feature_importances", {})
        if fi:
            sorted_feats = sorted(fi.items(), key=lambda x: x[1], reverse=True)
            feats = [f[0] for f in sorted_feats]
            vals = [f[1] for f in sorted_feats]
            total = sum(vals) or 1
            pct = [v / total * 100 for v in vals]
            fig_all_imp.add_trace(go.Bar(
                name=name, x=feats, y=pct,
                marker_color=model_colors[name], opacity=0.85,
            ))
    fig_all_imp.update_layout(
        **PLOTLY_LAYOUT, height=380, barmode="group",
        xaxis=dict(tickangle=-30, gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title="Importance (%)", gridcolor="rgba(255,255,255,0.05)"),
        legend=dict(font=dict(color="#E2E8F0"), bgcolor="rgba(0,0,0,0)"),
    )  # xaxis/yaxis safe: not in PLOTLY_LAYOUT
    st.plotly_chart(fig_all_imp, use_container_width=True)
