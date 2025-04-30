# Last modified: 2025-04-29 09:24:33
# Version: 0.0.1
import cv2
import supervision as sv
from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES

model = RFDETRBase()

cap = cv2.VideoCapture(<RTSP_STREAM_URL>)
while True:
    success, frame = cap.read()
    if not success:
        break

    detections = model.predict(frame[:, :, ::-1], threshold=0.5)
    
    labels = [
        f"{COCO_CLASSES[class_id]} {confidence:.2f}"
        for class_id, confidence
        in zip(detections.class_id, detections.confidence)
    ]

    annotated_frame = frame.copy()
    annotated_frame = sv.BoxAnnotator().annotate(annotated_frame, detections)
    annotated_frame = sv.LabelAnnotator().annotate(annotated_frame, detections, labels)

    cv2.imshow("RTSP Stream", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()