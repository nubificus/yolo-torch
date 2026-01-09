# YOLO Inference

This repository contains a YOLOv8n TorchScript model and example programs for
running object detection using:

- native LibTorch (stock)
- vAccel Torch plugin

## Build
```bash
mkdir build
cd build
cmake ..
make
```

## Stock
```bash
./yolo-stock ../yolov8n.torchscript ../bus.jpg
```

## vAccel
```bash
./yolo-vaccel ../yolov8n.torchscript ../bus.jpg
```
