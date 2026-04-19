"""
app.py - MediAI Flask Backend (Render)
- Memory optimised: loads pre-trained model only, never trains
- CORS enabled for Netlify frontend
- Starts instantly on port
"""
import os, sys, warnings, gc
warnings.filterwarnings("ignore")

ML_PROJECT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "disease_prediction")
sys.path.insert(0, ML_PROJECT)

from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates", static_folder="static")

# ── CORS: allow Netlify and any origin to call this API ──────────────────────
try:
    from flask_cors import CORS
    CORS(app)
    print("✅ CORS enabled")
except ImportError:
    # Manually add CORS headers if flask-cors not available
    @app.after_request
    def add_cors(response):
        response.headers["Access-Control-Allow-Origin"]  = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response
    print("⚠ flask-cors not found — using manual CORS headers")

# ── Handle OPTIONS preflight requests ─────────────────────────────────────────
@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        res = app.make_response("")
        res.headers["Access-Control-Allow-Origin"]  = "*"
        res.headers["Access-Control-Allow-Headers"] = "Content-Type"
        res.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return res

# ── Load pre-trained model ────────────────────────────────────────────────────
predictor  = None
load_error = None

def load_model():
    global predictor, load_error
    MODEL_PATH = os.path.join(ML_PROJECT, "models", "best_model.pkl")
    if not os.path.exists(MODEL_PATH):
        load_error = "Model not found. Push models/ folder to GitHub."
        print(f"❌ {load_error}")
        return
    try:
        from src.predictor import DiseasePredictor
        predictor = DiseasePredictor(models_dir=os.path.join(ML_PROJECT, "models"))
        gc.collect()
        print(f"✅ Model loaded — {len(predictor.get_all_diseases())} diseases, "
              f"{len(predictor.get_all_symptoms())} symptoms")
    except Exception as e:
        load_error = str(e)
        print(f"❌ Load error: {e}")

load_model()

# ═══════════════════════════════════════════════════════════════════════════════
# Pages (for Render-hosted frontend)
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
# API Endpoints
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

@app.route("/api/predict", methods=["POST", "OPTIONS"])
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
        gc.collect()
        return jsonify(r)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🏥 MediAI API → http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)