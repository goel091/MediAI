"""
app/streamlit_app.py
─────────────────────────────────────────────
Streamlit Web Application — AI Disease Prediction

Features:
  • Symptom multi-select with search
  • Real-time prediction with confidence gauge
  • Top-5 disease probability bar chart
  • Risk level indicator
  • SHAP explanation for predictions
  • EDA & model comparison dashboard tabs
─────────────────────────────────────────────

Run:
    streamlit run app/streamlit_app.py
─────────────────────────────────────────────
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ── Ensure project root is importable ─────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="MediAI — Disease Prediction System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }
  .main-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    background: linear-gradient(135deg, #1A73E8 0%, #0D47A1 50%, #6200EA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0;
  }
  .sub-title {
    text-align: center;
    color: #5F6368;
    font-size: 1.05rem;
    margin-top: 4px;
    margin-bottom: 2rem;
    font-weight: 300;
  }
  .metric-card {
    background: linear-gradient(135deg, #f8f9ff 0%, #e8f0fe 100%);
    border: 1px solid #c5cae9;
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin: 0.5rem 0;
  }
  .risk-high   { background: linear-gradient(135deg, #ffeaea, #ffe0e0); border-color: #ef9a9a; }
  .risk-medium { background: linear-gradient(135deg, #fff8e1, #fff3cd); border-color: #ffe082; }
  .risk-low    { background: linear-gradient(135deg, #e8f5e9, #f1f8e9); border-color: #a5d6a7; }

  .disease-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1A73E8, #0D47A1);
    color: white;
    border-radius: 24px;
    padding: 6px 18px;
    font-size: 1.15rem;
    font-weight: 600;
    margin: 8px 0;
  }
  .section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #1A237E;
    border-bottom: 2px solid #E8EAF6;
    padding-bottom: 8px;
    margin: 1.5rem 0 1rem;
  }
  .stMultiSelect [data-baseweb="tag"] {
    background-color: #1A73E8 !important;
    color: white !important;
    border-radius: 20px !important;
  }
  .sidebar .sidebar-content { background: #F0F4FF; }
  div[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D47A1 0%, #1565C0 100%); }
  div[data-testid="stSidebar"] * { color: white !important; }
  div[data-testid="stSidebar"] .stSelectbox label,
  div[data-testid="stSidebar"] .stMultiSelect label { color: #C5CAE9 !important; }

  .disclaimer {
    background: #FFF8E1;
    border-left: 4px solid #FFC107;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #5D4037;
    margin-top: 1rem;
  }
</style>
""", unsafe_allow_html=True)


# ── Load Predictor (cached) ────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading AI model …")
def load_predictor():
    """Load the saved predictor. Falls back to training if needed."""
    try:
        from src.predictor import DiseasePredictor
        predictor = DiseasePredictor(models_dir=os.path.join(ROOT, "models"))
        return predictor, None
    except FileNotFoundError:
        return None, "Model not found. Please run `python train_pipeline.py` first."
    except Exception as e:
        return None, str(e)


@st.cache_data(show_spinner=False)
def load_eda_data():
    """Load raw data for EDA dashboard tab."""
    raw_path = os.path.join(ROOT, "data", "raw", "disease_dataset.csv")
    if os.path.exists(raw_path):
        return pd.read_csv(raw_path)
    return None


@st.cache_data(show_spinner=False)
def load_comparison():
    """Load model comparison CSV."""
    path = os.path.join(ROOT, "notebooks", "model_comparison.csv")
    if os.path.exists(path):
        return pd.read_csv(path, index_col=0)
    return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def risk_color(level: str) -> str:
    return {"High": "#EA4335", "Medium": "#FBBC04", "Low": "#34A853"}.get(level, "#999")

def confidence_gauge(value: float, title: str = "Confidence") -> go.Figure:
    """Plotly gauge chart for prediction confidence."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": title, "font": {"size": 18, "family": "DM Sans"}},
        number={"suffix": "%", "font": {"size": 28}},
        gauge={
            "axis":       {"range": [0, 100], "tickwidth": 1},
            "bar":        {"color": "#1A73E8"},
            "bgcolor":    "white",
            "borderwidth": 2,
            "bordercolor": "#c5cae9",
            "steps": [
                {"range": [0,  40],  "color": "#fce8e6"},
                {"range": [40, 70],  "color": "#fef7e0"},
                {"range": [70, 100], "color": "#e6f4ea"},
            ],
            "threshold": {
                "line":  {"color": "#1A73E8", "width": 4},
                "thickness": 0.75,
                "value": value,
            },
        },
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def top_k_bar_chart(top_preds: list[tuple]) -> go.Figure:
    """Horizontal bar chart of top-K disease predictions."""
    diseases = [p[0] for p in top_preds]
    probs    = [p[1] for p in top_preds]
    colors   = px.colors.sequential.Blues_r[:len(diseases)]

    fig = go.Figure(go.Bar(
        x=probs,
        y=diseases,
        orientation="h",
        marker_color=[
            "#1A73E8" if i == 0 else "#90CAF9"
            for i in range(len(diseases))
        ],
        text=[f"{p:.1f}%" for p in probs],
        textposition="outside",
    ))
    fig.update_layout(
        title="Top Disease Predictions",
        xaxis_title="Probability (%)",
        yaxis={"autorange": "reversed"},
        xaxis={"range": [0, max(probs) * 1.25]},
        height=max(250, len(top_preds) * 55),
        margin=dict(l=10, r=80, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#F8F9FA",
        font_family="DM Sans",
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown('<h1 class="main-title">🏥 MediAI — Disease Prediction System</h1>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-title">AI-powered symptom analysis · Built with Machine Learning · '
        'Educational use only</p>',
        unsafe_allow_html=True
    )

    # ── Load resources ────────────────────────────────────────────────────────
    predictor, load_error = load_predictor()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        top_k   = st.slider("Top K Predictions", min_value=3, max_value=10, value=5)
        show_shap = st.checkbox("Show SHAP Explanation", value=False)
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown(
            "This tool uses an ML model trained on a **synthetic** symptom dataset "
            "to predict possible diseases. **Always consult a doctor.**"
        )
        st.markdown("---")
        if predictor:
            st.markdown(f"**Model loaded:** ✅")
            st.markdown(f"**Diseases:** {len(predictor.get_all_diseases())}")
            st.markdown(f"**Symptoms:** {len(predictor.get_all_symptoms())}")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_predict, tab_eda, tab_models, tab_about = st.tabs([
        "🔍 Predict Disease",
        "📊 Data Insights",
        "🤖 Model Performance",
        "📖 About",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1: PREDICTION
    # ══════════════════════════════════════════════════════════════════════════
    with tab_predict:
        if load_error:
            st.error(f"❌ {load_error}")
            st.info("💡 Run `python train_pipeline.py` from the project root to train the model.")
            return

        all_symptoms = predictor.get_all_symptoms()
        # Format for display
        display_symptoms = [s.replace("_", " ").title() for s in all_symptoms]
        sym_map = dict(zip(display_symptoms, all_symptoms))

        col_left, col_right = st.columns([1, 1], gap="large")

        with col_left:
            st.markdown('<p class="section-header">🩺 Patient Symptoms</p>',
                        unsafe_allow_html=True)

            selected_display = st.multiselect(
                "Select all symptoms the patient is experiencing:",
                options=display_symptoms,
                default=[],
                placeholder="Type to search symptoms …",
                help="Choose as many symptoms as applicable for a more accurate prediction.",
            )
            selected_raw = [sym_map[d] for d in selected_display]

            st.caption(f"**{len(selected_raw)}** symptom(s) selected")

            if selected_raw:
                st.markdown("**Active Symptoms:**")
                # Display as chips using columns
                cols = st.columns(3)
                for i, sym in enumerate(selected_display):
                    with cols[i % 3]:
                        st.markdown(
                            f"<span style='background:#E8F0FE;border:1px solid #C5CAE9;"
                            f"border-radius:20px;padding:3px 10px;font-size:0.8rem;"
                            f"color:#1A73E8;'>{sym}</span>",
                            unsafe_allow_html=True
                        )

            st.markdown("")
            predict_btn = st.button(
                "🔍 Predict Disease",
                type="primary",
                use_container_width=True,
                disabled=(len(selected_raw) == 0),
            )

            if not selected_raw:
                st.info("👆 Select at least one symptom to get a prediction.")

        with col_right:
            if predict_btn and selected_raw:
                with st.spinner("Analysing symptoms …"):
                    try:
                        result = predictor.predict(selected_raw, top_k=top_k)
                    except Exception as e:
                        st.error(f"Prediction error: {e}")
                        return

                st.markdown('<p class="section-header">📋 Prediction Results</p>',
                            unsafe_allow_html=True)

                # ── Primary result ──
                risk   = result["risk_level"]
                r_col  = risk_color(risk)
                r_class = f"risk-{risk.lower()}"

                st.markdown(
                    f'<div class="metric-card {r_class}">'
                    f'<div style="font-size:0.85rem;color:#555;font-weight:500;">PRIMARY DIAGNOSIS</div>'
                    f'<div class="disease-badge">{result["primary_disease"]}</div><br>'
                    f'<div style="font-size:0.85rem;color:#555;">'
                    f'Risk Level: <strong style="color:{r_col};">{risk}</strong>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

                # ── Confidence gauge ──
                fig_gauge = confidence_gauge(result["confidence"])
                st.plotly_chart(fig_gauge, use_container_width=True)

                # ── Top-K bar chart ──
                fig_bar = top_k_bar_chart(result["top_predictions"])
                st.plotly_chart(fig_bar, use_container_width=True)

                # ── Disclaimer ──
                st.markdown(
                    '<div class="disclaimer">⚠️ <strong>Medical Disclaimer:</strong> '
                    'This prediction is for educational purposes only and should '
                    'NOT replace professional medical advice. Always consult a '
                    'qualified healthcare provider.</div>',
                    unsafe_allow_html=True
                )

                # ── SHAP (if enabled + available) ──
                if show_shap:
                    st.markdown('<p class="section-header">🔬 Model Explanation (SHAP)</p>',
                                unsafe_allow_html=True)
                    shap_path = os.path.join(
                        ROOT, "notebooks", "shap_plots", "13_shap_bar_global.png"
                    )
                    if os.path.exists(shap_path):
                        st.image(shap_path, caption="Global SHAP Feature Importance",
                                 use_column_width=True)
                    else:
                        st.info("Run `python train_pipeline.py` to generate SHAP plots.")

            elif not predict_btn:
                # Placeholder
                st.markdown('<p class="section-header">📋 Prediction Results</p>',
                            unsafe_allow_html=True)
                st.markdown(
                    """
                    <div style="text-align:center;padding:3rem 1rem;color:#9AA0A6;">
                      <div style="font-size:4rem;">🩺</div>
                      <div style="font-size:1.1rem;margin-top:1rem;">
                        Select symptoms and click <strong>Predict Disease</strong>
                      </div>
                      <div style="font-size:0.9rem;margin-top:0.5rem;">
                        Our AI model will analyse your symptoms and suggest likely diagnoses.
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2: EDA DASHBOARD
    # ══════════════════════════════════════════════════════════════════════════
    with tab_eda:
        st.markdown('<p class="section-header">📊 Exploratory Data Analysis</p>',
                    unsafe_allow_html=True)

        df = load_eda_data()
        if df is None:
            st.warning("No data found. Run `python train_pipeline.py` first.")
        else:
            # ── Summary metrics ──
            symptom_cols = [c for c in df.columns if c != "Disease"]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Samples",  f"{len(df):,}")
            m2.metric("Diseases",       df["Disease"].nunique())
            m3.metric("Symptoms",       len(symptom_cols))
            m4.metric("Missing Values", f'{df.isnull().mean().mean()*100:.1f}%')

            st.markdown("---")
            c1, c2 = st.columns(2)

            with c1:
                # Disease distribution
                counts = df["Disease"].value_counts().reset_index()
                counts.columns = ["Disease", "Count"]
                fig_dist = px.bar(
                    counts, x="Count", y="Disease",
                    orientation="h",
                    title="Disease Distribution",
                    color="Count",
                    color_continuous_scale="Blues",
                )
                fig_dist.update_layout(
                    height=500, showlegend=False,
                    yaxis={"autorange": "reversed"},
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_dist, use_container_width=True)

            with c2:
                # Top symptoms
                sym_freq = df[symptom_cols].sum().sort_values(ascending=False).head(20)
                fig_sym = px.bar(
                    x=sym_freq.values,
                    y=sym_freq.index,
                    orientation="h",
                    title="Top 20 Most Frequent Symptoms",
                    color=sym_freq.values,
                    color_continuous_scale="Teal",
                )
                fig_sym.update_layout(
                    height=500, showlegend=False,
                    yaxis={"autorange": "reversed"},
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_sym, use_container_width=True)

            # ── Saved plots ──
            plots_dir = os.path.join(ROOT, "notebooks", "eda_plots")
            plot_files = {
                "Correlation Heatmap":        "03_correlation_heatmap.png",
                "Disease–Symptom Profile":    "04_disease_symptom_heatmap.png",
                "Class Balance":              "05_class_balance.png",
                "Symptom Co-occurrence":      "06_symptom_cooccurrence.png",
            }
            available = {k: os.path.join(plots_dir, v)
                         for k, v in plot_files.items()
                         if os.path.exists(os.path.join(plots_dir, v))}

            if available:
                st.markdown("### Saved EDA Plots")
                selected_plot = st.selectbox("Choose plot:", list(available.keys()))
                st.image(available[selected_plot], use_column_width=True)
            else:
                st.info("Run `python train_pipeline.py` to generate EDA plots.")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3: MODEL PERFORMANCE
    # ══════════════════════════════════════════════════════════════════════════
    with tab_models:
        st.markdown('<p class="section-header">🤖 Model Performance Comparison</p>',
                    unsafe_allow_html=True)

        comp_df = load_comparison()
        if comp_df is not None:
            # Highlight table
            styled = comp_df.style.background_gradient(
                cmap="Blues", subset=["Accuracy", "F1 (weighted)", "ROC-AUC", "CV Mean F1"]
            ).format("{:.4f}", subset=["Accuracy","Precision","Recall",
                                       "F1 (weighted)","ROC-AUC","CV Mean F1","CV Std"])
            st.dataframe(styled, use_container_width=True)

            st.markdown("---")
            # Radar chart
            metrics = ["Accuracy", "Precision", "Recall", "F1 (weighted)"]
            available_metrics = [m for m in metrics if m in comp_df.columns]
            fig_radar = go.Figure()
            colors_r = ["#1A73E8", "#34A853", "#EA4335", "#FBBC04"]
            for idx, (model_name, row) in enumerate(comp_df.iterrows()):
                vals = [row.get(m, 0) for m in available_metrics]
                vals += [vals[0]]  # close the loop
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals,
                    theta=available_metrics + [available_metrics[0]],
                    fill="toself",
                    name=model_name,
                    line_color=colors_r[idx % len(colors_r)],
                    opacity=0.7,
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title="Model Performance Radar Chart",
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        else:
            st.info("Run the training pipeline first to generate model comparison data.")

        # ── Saved model plots ──
        model_plots_dir = os.path.join(ROOT, "notebooks", "model_plots")
        model_plot_files = {
            "Model Comparison":     "07_model_comparison.png",
            "Confusion Matrices":   "08_confusion_matrices.png",
            "ROC Curves":           "09_roc_curves.png",
            "CV Comparison":        "10_cv_comparison.png",
            "Feature Importance":   "11_feature_importance.png",
        }
        avail_m = {k: os.path.join(model_plots_dir, v)
                   for k, v in model_plot_files.items()
                   if os.path.exists(os.path.join(model_plots_dir, v))}
        if avail_m:
            st.markdown("### Detailed Evaluation Plots")
            sel = st.selectbox("Choose plot:", list(avail_m.keys()), key="model_plot_sel")
            st.image(avail_m[sel], use_column_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4: ABOUT
    # ══════════════════════════════════════════════════════════════════════════
    with tab_about:
        st.markdown("""
## 🏥 About MediAI — Disease Prediction System

### Overview
MediAI is a production-grade, end-to-end Machine Learning project that predicts diseases
based on patient-reported symptoms. It is designed as a portfolio showcase demonstrating
real-world data science, ML engineering, and software development skills.

### 🛠️ Tech Stack
| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| ML Framework | Scikit-learn, XGBoost |
| Explainability | SHAP |
| Web App | Streamlit |
| Visualisation | Plotly, Matplotlib, Seaborn |
| Model Persistence | Joblib |
| Logging | Python `logging` |

### 🤖 Models Trained
- **K-Nearest Neighbours (KNN)** — Distance-based lazy learner
- **Logistic Regression** — Probabilistic linear classifier
- **Random Forest** — Ensemble of decision trees
- **XGBoost** — Gradient-boosted trees (typically best performer)

### 📂 Project Structure
```
disease_prediction/
├── data/
│   ├── raw/                  ← original dataset
│   └── processed/            ← scaled train/test splits
├── notebooks/
│   ├── eda_plots/            ← EDA visualisations
│   ├── model_plots/          ← evaluation plots
│   └── shap_plots/           ← SHAP explanations
├── src/
│   ├── logger.py             ← logging config
│   ├── data_generator.py     ← synthetic data
│   ├── data_preprocessing.py ← cleaning, scaling
│   ├── eda.py                ← EDA module
│   ├── model_trainer.py      ← training & evaluation
│   ├── explainability.py     ← SHAP wrapper
│   └── predictor.py          ← inference API
├── models/                   ← saved model artefacts
├── app/
│   └── streamlit_app.py      ← this file
├── train_pipeline.py         ← master training script
├── requirements.txt
└── README.md
```

### ⚠️ Disclaimer
This tool is for **educational and portfolio purposes only**.
It should **never** be used to replace professional medical diagnosis.
Always consult a licensed healthcare provider for medical decisions.

---
*Built with ❤️ as an AI/ML portfolio project.*
        """)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
