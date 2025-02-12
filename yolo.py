from ultralytics import YOLO

torchscript_model = YOLO("yolov8n.torchscript")

results = torchscript_model("bus.jpg")
