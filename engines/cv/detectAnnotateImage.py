# Last modified: 2025-04-29 22:23:12
# Version: 0.0.11
from rfdetr import RFDETRBase, RFDETRLarge
from rfdetr.util.coco_classes import COCO_CLASSES
import supervision as sv
import random
import string
from PIL import Image

model = RFDETRBase()


def generate_guid8():
    chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return "".join(random.choices(chars, k=8))


def annotateImageObj(image_path):

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

    image = Image.open(image_path)

    detections = model.predict(image, threshold=0.51)

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
    randName = generate_guid8()
    savedImagePath = f"/ai/bennwittRepos/CloverCatcher/app/tmpfiles/{randName}.png"
    annotated_image.save(savedImagePath)
    return annotated_image
