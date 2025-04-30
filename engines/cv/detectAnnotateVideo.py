# Last modified: 2025-04-29 18:07:44
# Version: 0.0.34
from rfdetr import RFDETRBase
import supervision as sv
from PIL import Image
import cv2

CLOVER_CLASSES = {
    0: "LuckyClover",
    1: "4-leaf Clover",
    2: "5-leaf Clover",
}

checkpointpath = "/ai/bennwittRepos/CloverCatcher/dataPuddle/trainingArtifacts/CloverCatcher_20250429-113902"
model = RFDETRBase(
    pretrained_weights=checkpointpath,
    device="cuda",
)

box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()


def callback(frame, index):
    rgb_frame = frame[:, :, ::-1].copy()
    detections = model.predict(rgb_frame, threshold=0.51)

    # Labels for detections
    labels = [
        f"{CLOVER_CLASSES.get(class_id, f'Unknown({class_id})')} {conf:.2f}"
        for class_id, conf in zip(detections.class_id, detections.confidence)
    ]

    LUCKY_IDS = {1, 2}  # IDs representing 4- and 5-leaf clovers

    if any(int(cls) in LUCKY_IDS for cls in detections.class_id):
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
        16.0,
        (0, 255, 0),
        8,
        cv2.LINE_AA,
    )

    return annotated


sv.process_video(
    source_path="/ai/bennwittRepos/CloverCatcher/dataPuddle/media/clover.mp4",
    target_path="/ai/bennwittRepos/CloverCatcher/dataPuddle/media/cloverCatcher-clover.mp4",
    callback=callback,
)
