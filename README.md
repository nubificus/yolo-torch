# YOLO Torch - Clean Build with GPU Support

This project provides a clean, optimized build system for YOLO object detection using LibTorch with GPU support.

## Features

- **GPU Acceleration**: Automatic CUDA detection and support
- **Optimized Build**: Multi-stage compilation with release optimizations
- **Docker Support**: Multi-stage Dockerfile with GPU runtime
- **Clean Dependencies**: Minimal, well-defined requirements
- **Cross-Platform**: Works on Linux with optional CUDA support

## Quick Start

### Prerequisites

- **System**: Linux (Ubuntu 20.04+ recommended)
- **Compiler**: GCC 9+ or Clang 10+
- **CMake**: 3.16+
- **OpenCV**: 4.5+
- **LibTorch**: 2.0+ (auto-downloaded in Docker)
- **CUDA**: 11.0+ (optional, for GPU support)

### Option 1: Docker (Recommended)

```bash
# Build with GPU support
docker build -t yolo-torch .

# Run with GPU
docker run --gpus all -v $(pwd):/workspace yolo-torch yolo-stock model.torchscript image.jpg

# Run CPU only
docker run -v $(pwd):/workspace yolo-torch yolo-stock model.torchscript image.jpg
```

### Option 2: Native Build

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y build-essential cmake git libopencv-dev

# Build the project
./build.sh

# Run inference
./build/yolo-stock model.torchscript image.jpg
```

## Build Options

### Native Build Script

```bash
# Standard build
./build.sh

# Clean build (removes build directory)
./build.sh clean

# Manual CMake configuration
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=all
make -j$(nproc)
```

### CMake Options

- `-DCMAKE_BUILD_TYPE=Release|Debug`: Build type (default: Release)
- `-DCMAKE_CUDA_ARCHITECTURES=<arch>`: CUDA architectures (default: auto-detect)
- `-DCMAKE_PREFIX_PATH=<path>`: LibTorch installation path

## Project Structure

```
yolo-torch/
├── CMakeLists.txt          # Optimized build configuration
├── Dockerfile              # Multi-stage GPU-enabled Docker
├── build.sh                # Automated build script
├── requirements.txt        # Python dependencies
├── yolo-stock.cc           # Native LibTorch implementation
├── yolo-vaccel.cc          # vAccel plugin implementation
├── yolo.py                 # Python Ultralytics example
└── README.md               # This file
```

## GPU Support

The build system automatically detects and configures GPU support:

- **CUDA Detection**: Checks for `nvcc` and CUDA libraries
- **GPU Runtime**: Automatically uses CUDA if available
- **Fallback**: Gracefully falls back to CPU if GPU unavailable
- **Docker GPU**: Uses NVIDIA runtime for container GPU access

### GPU Status Check

```cpp
// In yolo-stock.cc:186
torch::Device device(torch::cuda::is_available() ? torch::kCUDA : torch::kCPU);
```

## Docker Features

### Multi-Stage Build

1. **Base Stage**: System dependencies and CUDA setup
2. **Builder Stage**: Compilation with all build tools
3. **Runtime Stage**: Minimal runtime with GPU libraries

### GPU Runtime

- Uses `nvidia/cuda:12.1-runtime` for minimal GPU runtime
- Includes all necessary CUDA libraries
- Supports NVIDIA Container Toolkit

### Build Commands

```bash
# Build for specific CUDA version
docker build --build-arg CUDA_VERSION=11.8 -t yolo-torch .

# Build without GPU (CPU only)
docker build --build-arg CUDA_VERSION=cpu -t yolo-torch-cpu .
```

## Performance Optimizations

### Compiler Optimizations

- Release mode with `-O3` optimizations
- Position Independent Code (PIC)
- CUDA architecture-specific optimizations

### Runtime Optimizations

- Automatic GPU memory management
- Efficient tensor operations
- Optimized image preprocessing

## Usage Examples

### C++ Native

```bash
# Stock LibTorch implementation
./yolo-stock yolov8n.torchscript bus.jpg

# vAccel implementation (if available)
./yolo-vaccel yolov8n.torchscript bus.jpg
```

### Python

```bash
# Using Ultralytics
python3 yolo.py
```

### Docker

```bash
# With GPU
docker run --gpus all -v $(pwd):/workspace yolo-torch yolo-stock model.torchscript image.jpg

# Interactive shell
docker run --gpus all -it -v $(pwd):/workspace yolo-torch bash
```

## Troubleshooting

### Common Issues

1. **CUDA Not Found**: Install CUDA toolkit or use CPU-only build
2. **LibTorch Missing**: Use Docker or install LibTorch manually
3. **OpenCV Issues**: Install `libopencv-dev` package
4. **Memory Errors**: Reduce batch size or use smaller models

### Debug Build

```bash
# Build with debug symbols
./build.sh
cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
make -j$(nproc)
```

### Verbose Build

```bash
# Verbose make output
make VERBOSE=1 -j$(nproc)
```

## Dependencies

### System Dependencies

- `build-essential`: Compiler and build tools
- `cmake`: Build system
- `libopencv-dev`: OpenCV development headers
- `cuda-toolkit`: CUDA development (optional)

### Python Dependencies

- `torch>=2.0.0`: PyTorch with CUDA support
- `torchvision>=0.15.0`: Computer vision utilities
- `opencv-python>=4.5.0`: OpenCV Python bindings
- `ultralytics>=8.0.0`: YOLO implementation
- `numpy>=1.21.0`: Numerical computing

### Runtime Libraries

- LibTorch C++ libraries
- CUDA runtime libraries (GPU only)
- OpenCV shared libraries

## License

This project follows the same license as the original YOLO implementation.