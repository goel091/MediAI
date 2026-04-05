"""
app.py — MediAI Flask Web Server
================================
Serves the frontend website AND exposes a /api/predict endpoint
that runs the real trained ML model.

Run:
    python app.py
    → http://localhost:5000
"""

import os, sys, json, warnings
warnings.filterwarnings("ignore")

# ── Make the ML project importable ────────────────────────────────────────────
ML_PROJECT = os.path.join(os.path.dirname(__file__), "..", "disease_prediction")
sys.path.insert(0, ML_PROJECT)

from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__, template_folder="templates", static_folder="static")

# ── Load model once at startup ─────────────────────────────────────────────────
predictor = None
load_error = None
try:
    from src.predictor import DiseasePredictor
    predictor = DiseasePredictor(
        models_dir=os.path.join(ML_PROJECT, "models")
    )
    print(f"✅  Model loaded — {len(predictor.get_all_diseases())} diseases, "
          f"{len(predictor.get_all_symptoms())} symptoms")
except Exception as e:
    load_error = str(e)
    print(f"⚠️  Model not loaded: {e}")
    print("    Run  python ../disease_prediction/train_pipeline.py  first.")


# ═══════════════════════════════════════════════════════════════════════════════
# Routes
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/symptoms", methods=["GET"])
def get_symptoms():
    """Returns the full list of symptom names."""
    if predictor is None:
        return jsonify({"error": load_error}), 503
    syms = sorted(predictor.get_all_symptoms())
    return jsonify({"symptoms": syms, "count": len(syms)})


@app.route("/api/diseases", methods=["GET"])
def get_diseases():
    """Returns the full list of disease names."""
    if predictor is None:
        return jsonify({"error": load_error}), 503
    diseases = sorted(predictor.get_all_diseases())
    return jsonify({"diseases": diseases, "count": len(diseases)})


@app.route("/api/predict", methods=["POST"])
def predict():
    """
    POST  /api/predict
    Body: { "symptoms": ["itching", "skin_rash", "fatigue"], "top_k": 5 }
    Returns full prediction result.
    """
    if predictor is None:
        return jsonify({"error": load_error, "model_ready": False}), 503

    data = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms", [])
    top_k    = int(data.get("top_k", 5))

    if not symptoms or not isinstance(symptoms, list):
        return jsonify({"error": "Provide a non-empty 'symptoms' list."}), 400

    try:
        result = predictor.predict(symptoms, top_k=top_k)
        result["model_ready"] = True
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "model_ready": False}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_ready": predictor is not None,
        "diseases": len(predictor.get_all_diseases()) if predictor else 0,
        "symptoms": len(predictor.get_all_symptoms()) if predictor else 0,
    })


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n🏥  MediAI Web Server")
    print("   → http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
