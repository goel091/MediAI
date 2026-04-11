"""
app.py — MediAI Flask (Memory-Optimised for Render Free Tier)
Strategy: NO training on server. Model files committed to GitHub.
Server only LOADS the pre-trained model — uses ~150 MB RAM max.
"""
import os, sys, warnings, gc
warnings.filterwarnings("ignore")

ML_PROJECT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "disease_prediction")
sys.path.insert(0, ML_PROJECT)

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # Allow Netlify frontend to call this API

# ── Load model at startup (fast — no training) ───────────────────────────────
predictor  = None
load_error = None

def load_model():
    global predictor, load_error
    MODEL_PATH = os.path.join(ML_PROJECT, "models", "best_model.pkl")
    if not os.path.exists(MODEL_PATH):
        load_error = "Model file not found. Please train locally and push models/ to GitHub."
        print(f"❌ {load_error}")
        return
    try:
        from src.predictor import DiseasePredictor
        predictor = DiseasePredictor(models_dir=os.path.join(ML_PROJECT, "models"))
        gc.collect()  # Free any unused memory after loading
        print(f"✅ Model loaded — {len(predictor.get_all_diseases())} diseases, "
              f"{len(predictor.get_all_symptoms())} symptoms")
    except Exception as e:
        load_error = str(e)
        print(f"❌ Model load error: {e}")

load_model()

# ═══════════════════════════════════════════════════════════════════════════════
# Pages
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def home(): return render_template("home.html")

@app.route("/diagnose")
def diagnose(): return render_template("diagnose.html")

@app.route("/result")
def result(): return render_template("result.html")

@app.route("/diseases")
def diseases(): return render_template("diseases.html")

@app.route("/how-it-works")
def how_it_works(): return render_template("how_it_works.html")

# ═══════════════════════════════════════════════════════════════════════════════
# API
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/health")
def health():
    return jsonify({
        "status":      "ok",
        "model_ready": predictor is not None,
        "error":       load_error,
        "diseases":    len(predictor.get_all_diseases()) if predictor else 0,
        "symptoms":    len(predictor.get_all_symptoms()) if predictor else 0,
    })

@app.route("/api/status")
def status():
    return jsonify({
        "ready":    predictor is not None,
        "training": False,
        "error":    load_error,
    })

@app.route("/api/symptoms")
def get_symptoms():
    if predictor is None:
        return jsonify({"error": load_error or "Model not ready"}), 503
    return jsonify({"symptoms": sorted(predictor.get_all_symptoms())})

@app.route("/api/diseases")
def get_diseases():
    if predictor is None:
        return jsonify({"error": load_error or "Model not ready"}), 503
    return jsonify({"diseases": sorted(predictor.get_all_diseases())})

@app.route("/api/predict", methods=["POST"])
def predict():
    if predictor is None:
        return jsonify({"error": load_error or "Model not loaded"}), 503
    data     = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms", [])
    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400
    try:
        r = predictor.predict(symptoms, top_k=int(data.get("top_k", 5)))
        r["model_ready"] = True
        gc.collect()  # Clean up after each prediction
        return jsonify(r)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🏥 MediAI → http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
