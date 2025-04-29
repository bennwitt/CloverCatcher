# Last modified: 2025-04-29 12:18:15
# Version: 0.0.1
import supervision as sv
from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES

model = RFDETRBase()

def callback(frame, index):
    detections = model.predict(frame[:, :, ::-1], threshold=0.5)
        
    labels = [
        f"{COCO_CLASSES[class_id]} {confidence:.2f}"
        for class_id, confidence
        in zip(detections.class_id, detections.confidence)
    ]

    annotated_frame = frame.copy()
    annotated_frame = sv.BoxAnnotator().annotate(annotated_frame, detections)
    annotated_frame = sv.LabelAnnotator().annotate(annotated_frame, detections, labels)
    return annotated_frame

sv.process_video(
    source_path=<SOURCE_VIDEO_PATH>,
    target_path=<TARGET_VIDEO_PATH>,
    callback=callback
)