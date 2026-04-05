# 🚀 MediAI Website — Deployment Guide

## ── Local (Fastest) ──────────────────────────────────

```bash
# 1. Ensure the ML model is trained
cd ../disease_prediction
python train_pipeline.py

# 2. Start the web server
cd ../mediai_website
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

---

## ── Docker ───────────────────────────────────────────

```bash
# From project root (parent of both folders)
docker build -f mediai_website/Dockerfile -t mediai-web .
docker run -p 5000:5000 mediai-web
# → http://localhost:5000
```

---

## ── Render.com (Free Cloud) ──────────────────────────

1. Push both `disease_prediction/` and `mediai_website/` to GitHub
2. Go to https://render.com → New Web Service
3. Connect your GitHub repo
4. Settings:
   - **Root Directory**: `mediai_website`
   - **Build Command**: `pip install -r requirements.txt && cd ../disease_prediction && pip install -r requirements.txt && python train_pipeline.py`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Done — Render auto-deploys on every git push

---

## ── Railway.app ──────────────────────────────────────

```bash
npm install -g railway
railway login
railway init
railway up
```

---

## ── HuggingFace Spaces ───────────────────────────────

1. Create a Space → SDK: **Gradio** or **Docker**
2. Upload all files
3. Set `app_file = app.py` in README metadata
4. Port: 7860

---

## ── AWS EC2 ──────────────────────────────────────────

```bash
# On your EC2 instance (Ubuntu)
git clone https://github.com/yourname/mediai.git
cd mediai/disease_prediction && python train_pipeline.py
cd ../mediai_website
pip install -r requirements.txt gunicorn
gunicorn app:app --bind 0.0.0.0:80 --workers 4 --daemon
```

Configure Security Group to allow port 80 inbound.

---

## ── Environment Variables ────────────────────────────

| Variable       | Default               | Description            |
|----------------|-----------------------|------------------------|
| `PORT`         | `5000`                | Server port            |
| `ML_PROJECT`   | `../disease_prediction` | Path to ML project   |
| `FLASK_ENV`    | `production`          | Flask environment      |
