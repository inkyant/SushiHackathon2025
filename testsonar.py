from ultralytics import YOLO
import cv2

INPUT_PATH  = "out.mp4"
OUTPUT_PATH = "out_annotated.mp4"

model = YOLO("FineTunedSonar.pt")

cap = cv2.VideoCapture(INPUT_PATH)
if not cap.isOpened():
    raise RuntimeError(f"Could not open {INPUT_PATH}")


fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


fourcc = cv2.VideoWriter_fourcc(*"mp4v") # type: ignore
writer = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (w, h))
if not writer.isOpened():
    raise RuntimeError("VideoWriter failed to open. Try a different fourcc (e.g., 'avc1').")

while True:
    ok, frame = cap.read()
    if not ok:
        break

    results = model.predict(source=frame, device=0, imgsz=640, conf=0.25, verbose=False)
    annotated = results[0].plot()


    writer.write(annotated)

    cv2.imshow("Fish detector", annotated)
    if cv2.waitKey(33) & 0xFF == 27: 
        break

cap.release()
writer.release()
cv2.destroyAllWindows()
print(f"Saved: {OUTPUT_PATH} ({w}x{h} @ {fps:.2f} FPS)")
