# Last modified: 2025-04-29 12:47:30
# Version: 0.0.1
import gradio as gr
import supervision as sv
import cv2
from rfdetr import RFDETRLarge
from rfdetr.util.coco_classes import COCO_CLASSES
from PIL import Image
import os

# CONFIG
CHECKPOINT_PATH = "checkpoints/best_ema.pt"
DEVICE = "cuda"
OUTPUT_VIDEO_PATH = "output/annotated_stream.mp4"
TEMP_FRAME_DIR = "tmp_frames"
os.makedirs(TEMP_FRAME_DIR, exist_ok=True)

# Custom class labels (update if needed)
CLOVER_CLASSES = ["4-leaf Clover", "5-leaf Clover"]

# Load model
model = RFDETRLarge.load_from_checkpoint(CHECKPOINT_PATH, device=DEVICE)
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()


# Inference on video function
def detect_video(video_path):
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc, fps, (width, height))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = frame[:, :, ::-1]
        detections = model.predict(rgb_frame, threshold=0.5)

        labels = [
            f"{CLOVER_CLASSES[class_id]} {conf:.2f}"
            for class_id, conf in zip(detections.class_id, detections.confidence)
        ]

        # HUD logic
        if any(cls in [0, 1] for cls in detections.class_id):
            status_text = "🍀 Luck Has Been Detected And Found!"
        else:
            status_text = "🌿 CloverCatcherActive"

        annotated = box_annotator.annotate(frame.copy(), detections)
        annotated = label_annotator.annotate(annotated, detections, labels)
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

        out.write(annotated)
        frame_idx += 1

    cap.release()
    out.release()
    return OUTPUT_VIDEO_PATH


# Gradio app
demo = gr.Interface(
    fn=detect_video,
    inputs=gr.Video(sources="webcam", label="🎥 Capture Clover Video", format="mp4"),
    outputs=gr.Video(label="🍀 Annotated Detection Output"),
    title="CloverCatcher Live-ish",
    description="Capture a short video via webcam. AI will find lucky clovers, annotate them, and let you know if luck has been detected!",
)

if __name__ == "__main__":
    demo.launch()
