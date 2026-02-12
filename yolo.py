import torch
import cv2
import numpy as np
from ultralytics import YOLO

# Check for CUDA availability and set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Load the YOLO model
try:
    torchscript_model = YOLO("yolov8n.torchscript")
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

# Run inference
try:
    results = torchscript_model("bus.jpg")
    print("Inference completed successfully")
    
    # Display results
    for i, result in enumerate(results):
        boxes = result.boxes
        if boxes is not None:
            print(f"Detected {len(boxes)} objects in image {i}")
            for j, box in enumerate(boxes):
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                print(f"  Object {j}: class={cls}, confidence={conf:.2f}")
        else:
            print(f"No objects detected in image {i}")
            
except Exception as e:
    print(f"Error during inference: {e}")
    exit(1)
