import cv2


imgs = []
paths = ["/content/e88d39f72dcb7e1b64762edaceacfd34.jpg"]

for path in paths:
    image = cv2.imread(path)
    image = cv2.resize(image, (1280, 900))
    imgs.append(image)



from ultralytics import YOLO
from huggingface_hub import hf_hub_download


model_path = hf_hub_download(repo_id="Daniil-Domino/yolo11x-dialectic", filename="model.pt")
text_detection = YOLO(model_path)

def yolo_result_to_boxes(res):
    return res.boxes.xyxy
