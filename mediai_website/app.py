"""
app.py — MediAI Flask Web Server (Multi-Page)
"""
import os, sys, warnings
warnings.filterwarnings("ignore")

ML_PROJECT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "disease_prediction")
sys.path.insert(0, ML_PROJECT)

from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates", static_folder="static")

predictor = None
load_error = None

MODEL_PATH = os.path.join(ML_PROJECT, "models", "best_model.pkl")
if not os.path.exists(MODEL_PATH):
    import subprocess
    print("Model not found — training now...")
    subprocess.run([sys.executable, "train_pipeline.py"], cwd=ML_PROJECT, check=True)

try:
    from src.predictor import DiseasePredictor
    predictor = DiseasePredictor(models_dir=os.path.join(ML_PROJECT, "models"))
    print(f"Model loaded — {len(predictor.get_all_diseases())} diseases")
except Exception as e:
    load_error = str(e)
    print(f"Model error: {e}")

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

@app.route("/api/symptoms")
def get_symptoms():
    if predictor is None: return jsonify({"error": load_error}), 503
    return jsonify({"symptoms": sorted(predictor.get_all_symptoms())})

@app.route("/api/diseases")
def get_diseases():
    if predictor is None: return jsonify({"error": load_error}), 503
    return jsonify({"diseases": sorted(predictor.get_all_diseases())})

@app.route("/api/predict", methods=["POST"])
def predict():
    if predictor is None: return jsonify({"error": load_error}), 503
    data = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms", [])
    if not symptoms: return jsonify({"error": "No symptoms provided"}), 400
    try:
        r = predictor.predict(symptoms, top_k=int(data.get("top_k", 5)))
        r["model_ready"] = True
        return jsonify(r)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/health")
def health():
    return jsonify({"status":"ok","model_ready": predictor is not None})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
