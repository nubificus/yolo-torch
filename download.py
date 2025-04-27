from ultralytics import YOLO
import sys
import os
import shutil
variant = sys.argv[1]
device = sys.argv[2]

# Load the YOLO11 model
model = YOLO(f"yolo{variant}.pt")

# Export the model to TorchScript format
model.export(format="torchscript",device=f"{device}",save=True)

# Default export location (YOLO saves it in the current directory)
default_export_path = f"yolo{variant}.torchscript"

# Define the custom export path
custom_export_path = f"yolo{variant}-{device}.torchscript"

# Move or rename the exported model to the desired location
if os.path.exists(default_export_path):
    shutil.move(default_export_path, custom_export_path)  # Move the file to the new location



# Load the exported TorchScript model
torchscript_model = YOLO(f"yolo{variant}-{device}.torchscript")

# Run inference
results = torchscript_model("https://ultralytics.com/images/bus.jpg")
