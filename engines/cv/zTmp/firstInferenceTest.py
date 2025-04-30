# Last modified: 2025-04-29 11:01:20
# Version: 0.0.9
from rfdetr import RFDETRBase
from rfdetr import RFDETRLarge
from rfdetr.util.coco_classes import COCO_CLASSES
import supervision as sv
import numpy as np
from PIL import Image
import os

# Load image
image_path = "/ai/bennwittRepos/CloverCatcher/dataPuddle/media/pugs.jpeg"
image = Image.open(image_path)

# Predict
model = RFDETRLarge()
# model = RFDETRBase()
detections = model.predict(image, threshold=0.5)

# Prepare annotators
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
text_scale = sv.calculate_optimal_text_scale(resolution_wh=image.size)
thickness = sv.calculate_optimal_line_thickness(resolution_wh=image.size)

bbox_annotator = sv.BoxAnnotator(color=color, thickness=thickness)
label_annotator = sv.LabelAnnotator(
    color=color, text_color=sv.Color.BLACK, text_scale=text_scale, smart_position=True
)

# Generate labels
labels = [
    f"{COCO_CLASSES[class_id]} {confidence:.2f}"
    for class_id, confidence in zip(detections.class_id, detections.confidence)
]

# Annotate image
annotated_image = image.copy()
annotated_image = bbox_annotator.annotate(annotated_image, detections)
annotated_image = label_annotator.annotate(annotated_image, detections, labels)

# Save annotated image
directory, filename = os.path.split(image_path)
new_filename = f"detected-{filename}"
save_path = os.path.join(directory, new_filename)
annotated_image.save(save_path)

print(f"Annotated image saved to: {save_path}")
