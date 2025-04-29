# Last modified: 2025-04-29 12:28:10
# Version: 0.0.2
from rfdetr import RFDETRLarge, RFDETRBase
import supervision as sv
from PIL import Image
import cv2

CLOVER_CLASSES = ["4-leaf Clover", "5-leaf Clover"]
# model = RFDETRBase.load_from_checkpoint("checkpoints/best_ema.pt", device="cuda")
model = RFDETRLarge.load_from_checkpoint("checkpoints/best_ema.pt", device="cuda")
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()


def callback(frame, index):
    rgb_frame = frame[:, :, ::-1]
    detections = model.predict(rgb_frame, threshold=0.5)

    # Labels for detections
    labels = [
        f"{CLOVER_CLASSES[class_id]} {conf:.2f}"
        for class_id, conf in zip(detections.class_id, detections.confidence)
    ]

    # Overlay: Check for luck (4-leaf or 5-leaf clover IDs)
    if any(cls in [0, 1] for cls in detections.class_id):
        status_text = "🍀 Luck Has Been Detected And Found!"
    else:
        status_text = "🌿 CloverCatcherActive"

    # Annotate image
    annotated = frame.copy()
    annotated = box_annotator.annotate(annotated, detections)
    annotated = label_annotator.annotate(annotated, detections, labels)

    # Add HUD text
    cv2.putText(
        annotated,
        status_text,
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    return annotated
