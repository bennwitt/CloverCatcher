# Last modified: 2025-04-29 10:37:58
# Version: 0.0.19
import gradio as gr
from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES
import supervision as sv
from PIL import Image
import os

# Load model
model = RFDETRBase()
color = sv.ColorPalette.from_hex(
    [
        "#ffff00",
        "#ff9b00",
        "#ff8080",
        "#ff66b2",
        "#ff66ff",
        "#b266ff",
        "#9999ff",
        "#3399ff",
        "#66ffff",
        "#33ff99",
        "#66ff66",
        "#99ff00",
    ]
)


def agentDirector(message, history):
    if not message["files"] and not message["text"]:
        history.append({"role": "user", "content": "Zilch/Nada"})
        history.append(
            {
                "role": "assistant",
                "content": "Looks like you didn't share any thoughts or files.",
            }
        )
        return history

    image_path = message["files"][0]
    image = Image.open(image_path)

    detections = model.predict(image, threshold=0.5)

    text_scale = sv.calculate_optimal_text_scale(resolution_wh=image.size)
    thickness = sv.calculate_optimal_line_thickness(resolution_wh=image.size)

    bbox_annotator = sv.BoxAnnotator(color=color, thickness=thickness)
    label_annotator = sv.LabelAnnotator(
        color=color,
        text_color=sv.Color.BLACK,
        text_scale=text_scale,
        smart_position=True,
    )

    labels = [
        f"{COCO_CLASSES[class_id]} {confidence:.2f}"
        for class_id, confidence in zip(detections.class_id, detections.confidence)
    ]

    annotated_image = image.copy()
    annotated_image = bbox_annotator.annotate(annotated_image, detections)
    annotated_image = label_annotator.annotate(annotated_image, detections, labels)

    # Now properly update the history
    history.append({"role": "user", "content": {"path": image_path}})
    history.append({"role": "assistant", "content": gr.Image(value=annotated_image)})

    return history


theme = gr.themes.Base(
    primary_hue="red",
    secondary_hue="stone",
    neutral_hue="stone",
    text_size="md",
    font=[
        gr.themes.GoogleFont("Montserrat"),
        gr.themes.GoogleFont("Zilla Slab"),
        "system-ui",
        "sans-serif",
    ],
    font_mono=[
        gr.themes.GoogleFont("Roboto Mono"),
        "ui-monospace",
        "Consolas",
        "monospace",
    ],
)


with gr.Blocks(
    title="CloverCatcher",
    theme=theme,
    fill_height=True,
    fill_width=True,
) as cloverCatcher:

    cloverCatcherChat = gr.ChatInterface(
        fn=agentDirector,
        autofocus=True,
        autoscroll=True,
        flagging_mode="manual",
        flagging_options=["👍🏼 Like", "😑 Meh", "👎🏼 DisLike"],
        flagging_dir="./dataPuddle/usrFlags",
        save_history=True,
        multimodal=True,
        fill_height=True,
        fill_width=False,
        stop_btn=True,
        show_progress="full",
        type="messages",
        title="🍀 CloverCatcher",
        description="Upload a photo — Get it detected and annotated!",
    )

if __name__ == "__main__":

    cloverCatcher.launch(
        server_port=8001,
        show_error=True,
        show_api=False,
        share=False,
        server_name="0.0.0.0",
    )
