# YOLO Inferce

The repository contains a YOLOv8n `torchscript`. It can be used to run the examples.

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
