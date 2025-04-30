# Last modified: 2025-04-29 13:07:04
# Version: 0.0.6
import supervision as sv
from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES

model = RFDETRBase(device="cuda")


def callback(frame, index):
    rgb_frame = frame[:, :, ::-1].copy()
    detections = model.predict(rgb_frame, threshold=0.5)

    labels = [
        f"{COCO_CLASSES[class_id]} {confidence:.2f}"
        for class_id, confidence in zip(detections.class_id, detections.confidence)
    ]

    annotated_frame = frame.copy()
    annotated_frame = sv.BoxAnnotator().annotate(annotated_frame, detections)
    annotated_frame = sv.LabelAnnotator().annotate(annotated_frame, detections, labels)
    return annotated_frame


sv.process_video(
    source_path="/ai/bennwittRepos/CloverCatcher/dataPuddle/media/clover.mp4",
    target_path="/ai/bennwittRepos/CloverCatcher/dataPuddle/media/annotated-clover.mp4",
    callback=callback,
)
