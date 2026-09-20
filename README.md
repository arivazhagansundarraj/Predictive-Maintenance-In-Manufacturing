# ⚙️ PredictIQ — Industrial IoT Predictive Maintenance Platform

> AI-powered predictive maintenance system for smart manufacturing plants, built on the **AI4I 2020 Predictive Maintenance Dataset**.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![ML](https://img.shields.io/badge/ML-XGBoost%20|%20LightGBM%20|%20CatBoost%20|%20RF-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Features

| Module | Description |
|--------|-------------|
| 🏠 **Home Dashboard** | Fleet KPIs, health gauge, failure mode analysis |
| 📊 **Dataset Insights** | Full EDA, sensor distributions, correlation heatmap, SMOTE analysis |
| 🏆 **Model Evaluation** | 4-model comparison, ROC/PR curves, confusion matrices, feature importance |
| 🔮 **Live Prediction** | Real-time failure probability from sensor inputs with downloadable report |
| 🚨 **Anomaly Detection** | Isolation Forest dashboard with scatter plots and alert tables |
| 🔧 **Maintenance Panel** | Batch fleet scoring with color-coded recommendations and CSV export |

---

## 🧠 ML Pipeline

### Models Trained
- **Random Forest** — 200 estimators, balanced class weights
- **XGBoost** — gradient boosting with scale_pos_weight
- **LightGBM** — fast gradient boosting
- **CatBoost** — categorical-friendly gradient boosting

### Feature Engineering
| Feature | Formula |
|---------|---------|
| Temperature Difference | Process temp − Air temp |
| Wear Rate | Tool wear ÷ Rotational speed |
| Mechanical Load Index | Torque × Tool wear ÷ 1000 |

### Class Imbalance
SMOTE (Synthetic Minority Oversampling) is applied to the training set to address the ~3.4% failure rate.

### Model Selection
Best model selected by harmonic mean of **Recall** and **ROC-AUC** to maximise failure detection sensitivity.

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.9+
- pip

### 1. Clone / Download
```bash
git clone https://github.com/your-username/predictiq.git
cd predictiq
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

> **First run**: Models are automatically trained on first launch (~60–90 seconds). Subsequent runs load cached models instantly.

---

## ☁️ Deployment

### Streamlit Cloud (Recommended)
1. Push the repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set `app.py` as the entry point
4. Deploy!

### Vercel (Redirect)
Update `vercel.json` with your Streamlit Cloud URL, then deploy to Vercel for a custom domain redirect.

### Docker (Self-hosting)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.headless=true"]
```

---

## 📁 Project Structure

```
├── Dataset/
│   └── ai4i2020.csv          # AI4I 2020 dataset
├── models/                    # Auto-generated model artefacts
│   ├── best_model.pkl
│   ├── scaler.pkl
│   ├── isolation_forest.pkl
│   └── model_metrics.json
├── src/
│   ├── data_processing.py     # Cleaning, feature engineering, SMOTE
│   ├── model_training.py      # 4-model training & evaluation
│   ├── anomaly_detection.py   # Isolation Forest
│   ├── feature_importance.py  # Importance extraction
│   ├── health_score.py        # Health score [0–100]
│   └── recommendation.py      # Maintenance recommendation engine
├── pages/
│   ├── 1_Home_Dashboard.py
│   ├── 2_Dataset_Insights.py
│   ├── 3_Model_Evaluation.py
│   ├── 4_Live_Prediction.py
│   ├── 5_Anomaly_Detection.py
│   └── 6_Maintenance_Recommendations.py
├── .streamlit/config.toml     # Dark theme config
├── app.py                     # Entry point
├── requirements.txt
└── vercel.json
```

---

## 📊 Dataset

**AI4I 2020 Predictive Maintenance Dataset** — UCI Machine Learning Repository

- 10,000 data points, 14 features
- 5 failure modes: TWF, HDF, PWF, OSF, RNF
- ~3.4% failure rate (highly imbalanced)

---

## 📄 License

MIT License — free to use, modify, and distribute.
