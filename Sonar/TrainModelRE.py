from ultralytics import YOLO
import cv2, torch
from pathlib import Path

WEIGHTS = "exp4-hyperver-diff-train-last.pt"
SAVE_NEW_WEIGHTS = True 
def get_names_dict(obj):
    names = getattr(obj, "names", None)
    if names is None:
        return None
    return {i: n for i, n in enumerate(names)} if isinstance(names, list) else dict(names)

def rename_label(names, old="fish", new="tuna"):
    return {k: (new if str(v).lower() == old.lower() else v) for k, v in names.items()}

def apply_names(model, names_dict):
    model.model.names = names_dict
    if hasattr(model, "predictor") and model.predictor is not None:
        try: model.predictor.model.names = names_dict
        except Exception: pass
        try: model.predictor.names = names_dict
        except Exception: pass

def persist_rename(yolo_obj, new_names, out_path):
    ckpt = getattr(yolo_obj, "ckpt", None)
    if isinstance(ckpt, dict):
        if "model" in ckpt and hasattr(ckpt["model"], "names"):
            ckpt["model"].names = new_names
        ckpt["names"] = {int(i): n for i, n in new_names.items()}
        torch.save(ckpt, out_path)
        return out_path
    try:
        ckpt = torch.load(WEIGHTS, map_location="cpu", weights_only=False)
    except Exception:
        from torch.serialization import add_safe_globals
        from ultralytics.nn.tasks import DetectionModel
        add_safe_globals([DetectionModel])
        ckpt = torch.load(WEIGHTS, map_location="cpu")  

    if isinstance(ckpt, dict):
        if "model" in ckpt and hasattr(ckpt["model"], "names"):
            ckpt["model"].names = new_names
        ckpt["names"] = {int(i): n for i, n in new_names.items()}

    torch.save(ckpt, out_path)
    return out_path



model = YOLO(WEIGHTS)
before = get_names_dict(model.model)
print("Before:", before)
if not before:
    raise RuntimeError("Could not read class names from model; aborting rename.")
after = rename_label(before, old="fish", new="FISH")
apply_names(model, after)
print("After :", after)


if SAVE_NEW_WEIGHTS:
    out_path = Path(WEIGHTS).with_name(Path(WEIGHTS).stem + "-tuna.pt")
    saved = persist_rename(model, after, out_path)
    print(f"[info] Saved renamed weights to: {saved}")

cap = cv2.VideoCapture("out.mp4")
while True:
    ok, frame = cap.read()
    if not ok:
        break
    results = model.predict(source=frame, imgsz=640, conf=0.25, verbose=False)
    for r in results:
        r.names = after
    annotated = results[0].plot()
    cv2.imshow("Fish detector (now Tuna)", annotated)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()
