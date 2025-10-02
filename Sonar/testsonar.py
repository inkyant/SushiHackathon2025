from ultralytics import YOLO
import cv2
import os
from typing import List, Dict, Any, Optional, Tuple

MODEL_PATH = "FineTunedSonar.pt"


def detect_on_image(
    image_path: str,
    model_path: str = MODEL_PATH,
    imgsz: int = 640,
    conf: float = 0.25,
    device: Optional[int] = 0,
    save_annotated_to: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Runs YOLO detection on a single image and returns structured detections.

    Returns (detections, annotated_image_path)
    - detections: list of {class_name, confidence, bbox[x1,y1,x2,y2]}
    - annotated_image_path: path to saved annotated image if requested
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    model = YOLO(model_path)
    results = model.predict(
        source=image_path, device=device, imgsz=imgsz, conf=conf, verbose=False
    )
    r0 = results[0]

    detections: List[Dict[str, Any]] = []
    names = r0.names if hasattr(r0, "names") else {}

    if r0.boxes is not None:
        for box in r0.boxes:
            cls_id = int(box.cls.item()) if hasattr(box.cls, "item") else int(box.cls)
            conf_v = (
                float(box.conf.item()) if hasattr(box.conf, "item") else float(box.conf)
            )
            xyxy = (
                box.xyxy[0].tolist() if hasattr(box.xyxy, "tolist") else list(box.xyxy)
            )
            detections.append(
                {
                    "class_id": cls_id,
                    "class_name": names.get(cls_id, str(cls_id)),
                    "confidence": conf_v,
                    "bbox": [float(x) for x in xyxy],
                }
            )

    annotated_path: Optional[str] = None
    if save_annotated_to:
        annotated = r0.plot()
        os.makedirs(os.path.dirname(save_annotated_to), exist_ok=True)
        cv2.imwrite(save_annotated_to, annotated)
        annotated_path = save_annotated_to

    return detections, annotated_path


def detect_on_video(
    input_path: str,
    output_path: str = "out_annotated.mp4",
    model_path: str = MODEL_PATH,
    imgsz: int = 640,
    conf: float = 0.25,
    device: Optional[int] = 0,
) -> str:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {input_path}")

    model = YOLO(model_path)

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    if not writer.isOpened():
        raise RuntimeError(
            "VideoWriter failed to open. Try a different fourcc (e.g., 'avc1')."
        )

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        results = model.predict(
            source=frame, device=device, imgsz=imgsz, conf=conf, verbose=False
        )
        annotated = results[0].plot()
        writer.write(annotated)

        cv2.imshow("Fish detector", annotated)
        if cv2.waitKey(33) & 0xFF == 27:
            break

    cap.release()
    writer.release()
    cv2.destroyAllWindows()
    return output_path


if __name__ == "__main__":
    # Example image inference
    img = "example_sonar_frame.jpg"
    try:
        dets, ann = detect_on_image(img, save_annotated_to="/tmp/sonar_annotated.jpg")
        print({"detections": dets, "annotated": ann})
    except FileNotFoundError as e:
        print(str(e))

    # Example video inference
    # out_video = detect_on_video("out.mp4")
    # print(f"Saved: {out_video}")
