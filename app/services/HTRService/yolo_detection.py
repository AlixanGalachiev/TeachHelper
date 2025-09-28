from ultralytics import YOLO
from huggingface_hub import hf_hub_download, login
import os

login(token=os.getenv("HUGGINGFACE_HUB_TOKEN"))

model_path = hf_hub_download(repo_id="Daniil-Domino/yolo11x-dialectic", filename="model.pt")
text_detection = YOLO(model_path)

def yolo_result_to_boxes(res):
    return res.boxes.xyxy
