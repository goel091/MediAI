# 🏥 MediAI — AI-Powered Disease Prediction System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.4-orange?logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-red)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit&logoColor=white)
![SHAP](https://img.shields.io/badge/SHAP-0.45-purple)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**A production-ready, end-to-end Machine Learning system that predicts diseases from patient symptoms — featuring model explainability, an interactive web app, and full CI/CD readiness.**

[🔍 Demo](#demo) · [🚀 Quick Start](#quick-start) · [📂 Structure](#project-structure) · [🤖 Models](#models) · [📊 Results](#results)

</div>

---

## 📌 Project Overview

MediAI is a complete data science portfolio project that demonstrates real-world ML engineering skills from raw data to a deployed web application. The system:

- Ingests and preprocesses a 40-disease, 132-symptom dataset
- Trains and compares **4 classifiers** (KNN, Logistic Regression, Random Forest, XGBoost)
- Selects the best model via cross-validation and hyperparameter tuning
- Provides **SHAP-based explanations** for individual predictions
- Serves predictions through a polished **Streamlit web application**
- Is fully containerised with **Docker**

> ⚠️ **Disclaimer**: This tool is for educational and portfolio purposes only. It must not be used for real medical diagnosis.

---

## 🎬 Demo

| Prediction Screen | EDA Dashboard | Model Performance |
|:-:|:-:|:-:|
| ![Prediction](.github/screenshots/prediction.png) | ![EDA](.github/screenshots/eda.png) | ![Models](.github/screenshots/models.png) |

*(Screenshots generated after running the app)*

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Language** | Python 3.11 |
| **ML** | Scikit-learn 1.4, XGBoost 2.0 |
| **Explainability** | SHAP 0.45 |
| **Web App** | Streamlit 1.35 |
| **Visualisation** | Plotly, Matplotlib, Seaborn |
| **Persistence** | Joblib |
| **Testing** | Pytest |
| **Containerisation** | Docker |
| **Logging** | Python `logging` (file + console) |

---

## 📂 Project Structure

```
disease_prediction/
│
├── 📁 data/
│   ├── raw/                        # Original / generated dataset
│   └── processed/                  # Scaled train/test splits
│
├── 📁 notebooks/
│   ├── eda_plots/                  # EDA visualisations (PNG)
│   ├── model_plots/                # Model evaluation plots (PNG)
│   ├── shap_plots/                 # SHAP explanation plots (PNG)
│   └── model_comparison.csv        # Model metrics table
│
├── 📁 src/
│   ├── logger.py                   # Centralized logging setup
│   ├── data_generator.py           # Synthetic dataset generation
│   ├── data_preprocessing.py       # Cleaning, encoding, scaling
│   ├── eda.py                      # EDA analysis & plots
│   ├── model_trainer.py            # Training, evaluation, tuning
│   ├── explainability.py           # SHAP wrapper
│   └── predictor.py                # Inference / prediction API
│
├── 📁 models/
│   ├── best_model.pkl              # Saved best classifier
│   ├── scaler.pkl                  # Fitted StandardScaler
│   ├── label_encoder.pkl           # Fitted LabelEncoder
│   └── metadata.pkl                # Feature/class name metadata
│
├── 📁 app/
│   └── streamlit_app.py            # Streamlit web application
│
├── 📁 tests/
│   └── test_pipeline.py            # Pytest unit tests
│
├── 📁 logs/                        # Auto-generated log files
│
├── train_pipeline.py               # 🏁 Master training script
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

---

## 🚀 Quick Start

### Option A — Local (Python)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/disease-prediction.git
cd disease-prediction

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the full training pipeline
python train_pipeline.py

# 5. Launch the web app
streamlit run app/streamlit_app.py
```

Then open your browser at **http://localhost:8501**

### Option B — Docker

```bash
# Build image (includes training)
docker build -t mediai .

# Run container
docker run -p 8501:8501 mediai

# Open http://localhost:8501
```

### Option C — Run Tests

```bash
pytest tests/ -v --tb=short
```

---

## 🤖 Models

Four classifiers are trained and compared:

| Model | Description | Strength |
|-------|-------------|----------|
| **KNN** | K-Nearest Neighbours | Simple, interpretable baseline |
| **Logistic Regression** | Probabilistic linear model | Fast, good on linearly separable data |
| **Random Forest** | Ensemble of 200 decision trees | Robust, handles non-linearity |
| **XGBoost** | Gradient-boosted trees | Best accuracy on structured/tabular data |

The best-performing model (typically **XGBoost** or **Random Forest**) is selected via:
1. Cross-validation (5-fold, stratified)
2. GridSearchCV hyperparameter tuning
3. Final test-set evaluation

---

## 📊 Results (Typical)

| Model | Accuracy | F1 (weighted) | ROC-AUC | CV Mean F1 |
|-------|----------|---------------|---------|------------|
| KNN | ~0.88 | ~0.87 | ~0.98 | ~0.86 |
| Logistic Regression | ~0.85 | ~0.84 | ~0.97 | ~0.83 |
| Random Forest | ~0.97 | ~0.97 | ~0.999 | ~0.96 |
| **XGBoost** | **~0.98** | **~0.98** | **~0.999** | **~0.97** |

> Results vary slightly with random seed and dataset generation parameters.

---

## 🔬 SHAP Explainability

Every prediction can be explained using SHAP values:

- **Global**: Which symptoms matter most for each disease class
- **Local**: Why the model predicted a specific disease for a given patient
- **Waterfall**: Step-by-step contribution of each symptom

---

## 📋 Pipeline Walkthrough

```
Raw Data → Clean → Encode → Scale → Train 4 Models
    → EDA → Evaluate (Accuracy/F1/ROC) → Cross-Validate
    → Tune Best Model (GridSearchCV) → SHAP Explanations
    → Save Artefacts → Deploy via Streamlit
```

---

## ☁️ Cloud Deployment

### Render (Free)
```bash
# 1. Push to GitHub
# 2. Connect repo on render.com
# 3. Set start command: streamlit run app/streamlit_app.py --server.port $PORT
```

### HuggingFace Spaces (Free)
```bash
# Create a Space with "Streamlit" SDK
# Upload all project files
# HuggingFace auto-detects requirements.txt
```

### AWS EC2
```bash
# On EC2 instance:
docker pull yourusername/mediai
docker run -d -p 80:8501 yourusername/mediai
```

---

## 🔧 Configuration

Key parameters in `train_pipeline.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_samples_per_disease` | 120 | Training samples per disease |
| `test_size` | 0.20 | Train/test split ratio |
| `cv_folds` | 5 | Cross-validation folds |
| `random_state` | 42 | Reproducibility seed |

---

## 🚧 Future Improvements

- [ ] Integrate real Kaggle/UCI dataset via API
- [ ] Add LIME explainability alongside SHAP
- [ ] REST API endpoint (FastAPI)
- [ ] Patient history tracking (SQLite)
- [ ] Multi-language support
- [ ] Mobile-responsive Progressive Web App
- [ ] Continuous training pipeline (MLflow / DVC)
- [ ] A/B testing between model versions

---

## 🧪 Running Tests

```bash
pytest tests/ -v                    # all tests
pytest tests/ -v -k "DataGenerator" # specific class
pytest tests/ --cov=src             # with coverage
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- Disease symptom dataset structure inspired by the **Kaggle Disease Symptom Prediction** dataset
- SHAP library by [Lundberg & Lee (2017)](https://arxiv.org/abs/1705.07874)

---

<div align="center">
  Built with ❤️ as an AI/ML Portfolio Project · <a href="https://github.com/goel091">goel091</a>
</div>
