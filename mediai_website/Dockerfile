# ─────────────────────────────────────────────
# MediAI Website — Dockerfile
# Build:  docker build -t mediai-web .
# Run:    docker run -p 5000:5000 mediai-web
# ─────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy ML project first
COPY ../disease_prediction /ml/disease_prediction

# Copy web app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Train model if not present
RUN cd /ml/disease_prediction && pip install --no-cache-dir -r requirements.txt \
 && python train_pipeline.py

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
