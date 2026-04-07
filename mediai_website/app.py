"""
app.py — MediAI Flask Web Server
Fixed for Render: server starts immediately, model trains in background thread.
"""
import os, sys, warnings, threading
warnings.filterwarnings("ignore")

ML_PROJECT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "disease_prediction")
sys.path.insert(0, ML_PROJECT)

from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates", static_folder="static")

# ── Global state ──────────────────────────────────────────────────────────────
predictor   = None
load_error  = None
is_training = False
training_done = False

# ── Background training function ──────────────────────────────────────────────
def train_and_load():
    global predictor, load_error, is_training, training_done
    is_training = True
    print("🔧 Background thread: checking model...")

    MODEL_PATH = os.path.join(ML_PROJECT, "models", "best_model.pkl")

    if not os.path.exists(MODEL_PATH):
        print("📊 Model not found — training now (this takes ~60 seconds)...")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "train_pipeline.py"],
                cwd=ML_PROJECT,
                capture_output=True,
                text=True,
                timeout=600  # 10 min max
            )
            if result.returncode != 0:
                load_error = f"Training failed: {result.stderr[-500:]}"
                print(f"❌ Training error: {load_error}")
                is_training = False
                return
            print("✅ Training complete!")
        except Exception as e:
            load_error = str(e)
            print(f"❌ Training exception: {e}")
            is_training = False
            return

    # Load predictor
    try:
        from src.predictor import DiseasePredictor
        predictor = DiseasePredictor(models_dir=os.path.join(ML_PROJECT, "models"))
        print(f"✅ Model loaded — {len(predictor.get_all_diseases())} diseases, {len(predictor.get_all_symptoms())} symptoms")
    except Exception as e:
        load_error = str(e)
        print(f"❌ Load error: {e}")

    is_training   = False
    training_done = True

# ── Start background training thread immediately ──────────────────────────────
t = threading.Thread(target=train_and_load, daemon=True)
t.start()
print("🚀 Flask server starting — model loading in background...")

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
        "status":        "ok",
        "model_ready":   predictor is not None,
        "is_training":   is_training,
        "training_done": training_done,
        "error":         load_error,
        "diseases":      len(predictor.get_all_diseases()) if predictor else 0,
        "symptoms":      len(predictor.get_all_symptoms()) if predictor else 0,
    })

@app.route("/api/status")
def status():
    """Called by frontend to check if model is ready yet."""
    return jsonify({
        "ready":      predictor is not None,
        "training":   is_training,
        "error":      load_error,
    })

@app.route("/api/symptoms")
def get_symptoms():
    if predictor is None:
        return jsonify({"error": "Model not ready yet. Please wait.", "training": is_training}), 503
    return jsonify({"symptoms": sorted(predictor.get_all_symptoms())})

@app.route("/api/diseases")
def get_diseases():
    if predictor is None:
        return jsonify({"error": "Model not ready yet.", "training": is_training}), 503
    return jsonify({"diseases": sorted(predictor.get_all_diseases())})

@app.route("/api/predict", methods=["POST"])
def predict():
    if predictor is None:
        return jsonify({
            "error":    "Model is still loading. Please wait a moment and try again.",
            "training": is_training
        }), 503
    data     = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms", [])
    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400
    try:
        r = predictor.predict(symptoms, top_k=int(data.get("top_k", 5)))
        r["model_ready"] = True
        return jsonify(r)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🏥  MediAI → http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)