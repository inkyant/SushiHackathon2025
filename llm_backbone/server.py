"""
Author: Kamran Hussain
Date: 2025-10-01

Server.py

Description:
Serve the LLM backbone model via vLLM. We need to create a vLLM server that can handle the LLM backbone model.
with a clean API facing the frontend.
"""

from flask import Flask, request, jsonify
from llm import LLMBackbone
from importlib import import_module
import json

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
llm = LLMBackbone()


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


if __name__ == "__main__":
    app.run(debug=True)
