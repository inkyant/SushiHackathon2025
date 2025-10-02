"""
Author: Kamran Hussain
Date: 2025-10-01

Server.py

Description:
Serve the LLM backbone model via vLLM. We need to create a vLLM server that can handle the LLM backbone model.
with a clean API facing the frontend.
"""

from flask import Flask, request, jsonify

try:
    # Optional CORS for local dev from CRA (port 3000)
    from flask_cors import CORS  # type: ignore
except Exception:
    CORS = None  # type: ignore
from importlib import import_module
import json
import os
import sys

# Ensure project root is on sys.path so imports like `Sonar.*` work when running this file directly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Lazy import sonar helper to avoid heavy load at startup
try:
    sonar_module = import_module("Sonar.testsonar")
    detect_on_image = getattr(sonar_module, "detect_on_image", None)
except Exception:
    sonar_module = None
    detect_on_image = None

try:
    maint_module = import_module("maintainance_model.run_maintainance")
    get_engine_fault = getattr(maint_module, "get_engine_fault", None)
except Exception:
    maint_module = None
    get_engine_fault = None

app = Flask(__name__)
if CORS is not None:
    CORS(app)

from openai_bridge import LLMBackbone as SelectedLLMBackbone  # type: ignore

llm = SelectedLLMBackbone()


@app.route("/infer", methods=["POST"])
def infer():
    data = request.json or {}
    image = data.get("image")
    text = data.get("text")
    pred_context = data.get("pred_context")
    output = llm.infer(image=image, text=text, pred_context=pred_context)
    return jsonify(
        {"output": (output[0] if isinstance(output, list) and output else output)}
    )


@app.route("/mm_infer", methods=["POST"])
def mm_infer():
    """
    Multimodal inference orchestration:
    Input JSON fields:
      - image_path: local path to sonar image
      - engine_stats: [rpm, oilP, fuelP, coolP, oilT, coolT]
      - context: { location, water_body, datetime, season, temperature }
      - save_annotated_to: optional output path for annotated sonar image
      - user_prompt: optional user instruction to steer the LLM
    """
    data = request.json or {}
    image_path = data.get("image_path")
    engine_stats = data.get("engine_stats")
    context = data.get("context", {})
    save_annotated_to = data.get("save_annotated_to")
    user_prompt = data.get("user_prompt")
    sensor_data = data.get("sensor_data") or {}
    anomalies = data.get("anomalies") or []

    # If no explicit image_path, try to infer from sensor_data
    if not image_path and isinstance(sensor_data, dict):
        try:
            image_path = sensor_data.get("sonar", {}).get(
                "imagePath"
            ) or sensor_data.get("sonar", {}).get("image_path")
        except Exception:
            image_path = None

    # If engine_stats are not provided or malformed, attempt derivation from sensor_data
    def _num(x):
        try:
            return float(x)
        except Exception:
            return 0.0

    if not (isinstance(engine_stats, list) and len(engine_stats) == 6):
        eng = (
            (sensor_data or {}).get("engine", {})
            if isinstance(sensor_data, dict)
            else {}
        )
        fuel = (
            (sensor_data or {}).get("fuel", {}) if isinstance(sensor_data, dict) else {}
        )
        # Expected order: rpm, oilP, fuelP, coolP, oilT, coolT
        engine_stats = [
            _num(eng.get("rpm", 0)),
            _num(eng.get("oilPressure", 0)),
            _num(fuel.get("pressure", 0)),
            _num(eng.get("coolantPressure", 0)),
            _num(eng.get("oilTemp", eng.get("temperature", 0))),
            _num(eng.get("coolantTemp", eng.get("temperature", 0))),
        ]

    sonar_info = {}
    annotated_image = None
    if detect_on_image and image_path:
        try:
            dets, ann_path = detect_on_image(
                image_path, save_annotated_to=save_annotated_to
            )
            annotated_image = ann_path or image_path
            # Summarize detections by class
            counts = {}
            for d in dets:
                name = d.get("class_name", str(d.get("class_id")))
                counts[name] = counts.get(name, 0) + 1
            sonar_info = {
                "detections": dets,
                "counts_by_class": counts,
                "annotated_image": annotated_image,
            }
        except Exception as e:
            sonar_info = {"error": f"Sonar detection failed: {str(e)}"}

    maint_info = {}
    if get_engine_fault and isinstance(engine_stats, list) and len(engine_stats) == 6:
        try:
            label, confidence, probs = get_engine_fault(engine_stats)
            maint_info = {
                "diagnosis": label,
                "confidence": float(confidence),
                "probabilities": [float(p) for p in probs],
            }
        except Exception as e:
            maint_info = {"error": f"Maintenance model failed: {str(e)}"}

    # Build pred_context text for LLM
    ctx_lines = []
    if context:
        ctx_lines.append(f"Context: {json.dumps(context)}")
    # Include anomaly summary if provided
    if anomalies:
        try:
            summary = [
                {
                    "type": a.get("type"),
                    "severity": a.get("severity"),
                    "value": a.get("value"),
                }
                for a in (anomalies if isinstance(anomalies, list) else [])
            ]
            ctx_lines.append(f"Anomalies: {json.dumps(summary)}")
        except Exception:
            pass
    # Include compact sensor snapshot
    if isinstance(sensor_data, dict) and sensor_data:
        try:
            snapshot = {
                "engine": {
                    "rpm": (sensor_data.get("engine", {}) or {}).get("rpm"),
                    "oilPressure": (sensor_data.get("engine", {}) or {}).get(
                        "oilPressure"
                    ),
                    "temperature": (sensor_data.get("engine", {}) or {}).get(
                        "temperature"
                    ),
                },
                "navigation": {
                    "speed": (sensor_data.get("navigation", {}) or {}).get("speed"),
                    "heading": (sensor_data.get("navigation", {}) or {}).get("heading"),
                    "depth": (sensor_data.get("navigation", {}) or {}).get("depth"),
                    "gps": (sensor_data.get("navigation", {}) or {}).get("gps"),
                },
            }
            ctx_lines.append(f"Sensors: {json.dumps(snapshot)}")
        except Exception:
            pass
    if sonar_info:
        sonar_ctx = {k: v for k, v in sonar_info.items() if k != "detections"}
        ctx_lines.append(f"Sonar summary: {json.dumps(sonar_ctx)}")
        # Include compact detection summary
        if "detections" in sonar_info:
            short = [
                {
                    "class": d.get("class_name", d.get("class_id")),
                    "conf": round(float(d.get("confidence", 0.0)), 3),
                }
                for d in sonar_info["detections"][:20]
            ]
            ctx_lines.append(f"Detections(head): {json.dumps(short)}")
    if maint_info:
        ctx_lines.append(f"Engine status: {json.dumps(maint_info)}")
    pred_context = "\n".join(ctx_lines) if ctx_lines else None

    # Choose image input for LLM
    llm_image = annotated_image or image_path
    output = llm.infer(image=llm_image, text=user_prompt, pred_context=pred_context)

    return jsonify(
        {
            "llm_output": (
                output[0] if isinstance(output, list) and output else output
            ),
            "sonar": sonar_info,
            "engine": maint_info,
        }
    )


@app.route("/health", methods=["GET"])
def health():
    """Lightweight health check for core components."""
    sonar_ok = detect_on_image is not None
    maint_ok = get_engine_fault is not None
    # Check weight file existence (best-effort)
    sonar_weights = None
    try:
        # Import inside to avoid hard dependency if module missing
        from Sonar.testsonar import MODEL_PATH as SONAR_MODEL

        sonar_weights = os.path.join(PROJECT_ROOT, "Sonar", SONAR_MODEL)
    except Exception:
        pass
    maint_weights = os.path.join(
        PROJECT_ROOT, "maintainance_model", "multiclass_model.pt"
    )

    return jsonify(
        {
            "status": "ok",
            "components": {
                "llm_loaded": True,
                "sonar_helper_available": sonar_ok,
                "maint_helper_available": maint_ok,
            },
            "weights": {
                "sonar_present": (
                    os.path.exists(sonar_weights) if sonar_weights else False
                ),
                "maint_present": os.path.exists(maint_weights),
            },
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("LLM_PORT", os.environ.get("PORT", 7001)))
    host = os.environ.get("LLM_HOST", "0.0.0.0")
    print("=" * 60)
    print("🤖 LLM BACKBONE SERVER")
    print("=" * 60)
    print(f"Starting Flask LLM server on {host}:{port}")
    print(f"Sonar detection available: {detect_on_image is not None}")
    print(f"Maintenance model available: {get_engine_fault is not None}")
    print("=" * 60)
    app.run(debug=True, host=host, port=port)
