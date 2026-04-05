# ─────────────────────────────────────────────
# Dockerfile — AI Disease Prediction System
# ─────────────────────────────────────────────
# Build:   docker build -t mediai .
# Run:     docker run -p 8501:8501 mediai
# ─────────────────────────────────────────────

FROM python:3.11-slim

# ── System dependencies ──────────────────────
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────
WORKDIR /app

# ── Install Python dependencies ───────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Copy project files ────────────────────────
COPY . .

# ── Create required directories ───────────────
RUN mkdir -p data/raw data/processed notebooks/eda_plots \
             notebooks/model_plots notebooks/shap_plots \
             models logs

# ── Train model on container startup ─────────
# (pre-train during build for faster start)
RUN python train_pipeline.py

# ── Expose Streamlit port ─────────────────────
EXPOSE 8501

# ── Health check ─────────────────────────────
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# ── Streamlit runtime config ──────────────────
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# ── Start app ─────────────────────────────────
CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
