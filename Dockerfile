# Optimized Dockerfile for YOLO Torch with PyTorch 2.8, OpenCV 4.10, and CUDA 12.8+
FROM nvcr.io/nvidia/cuda:12.8.0-devel-ubuntu22.04 AS base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_ARCHITECTURES=all
ENV TORCH_CUDA_ARCH_LIST="6.0;6.1;7.0;7.5;8.0;8.6;8.9;9.0"
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    pkg-config \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    software-properties-common \
    ninja-build \
    unzip \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Install LibTorch 2.8.0 using pip for better compatibility
RUN pip3 install --no-cache-dir torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cu124

# Set working directory
WORKDIR /workspace

# Copy source files
COPY . .

# Build C++ components using CMake
RUN cd /workspace && \
    mkdir -p build && \
    cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc) && \
    cd /workspace

# Install built binaries
RUN cp build/yolo-stock /usr/local/bin/ && \
    cp build/yolo-simple /usr/local/bin/ && \
    cp build/yolo-vaccel /usr/local/bin/ 2>/dev/null || true

# Create compatible test model
RUN python3 export-model.py

# Download sample files if not present
RUN test -f bus.jpg || wget -q https://ultralytics.com/images/bus.jpg -O bus.jpg
RUN test -f yolov8n.torchscript || wget -q https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.torchscript -O yolov8n.torchscript

# Update library cache
RUN ldconfig

# Copy comprehensive test script
COPY comprehensive-test.sh /workspace/
RUN chmod +x /workspace/comprehensive-test.sh

# Set runtime environment
ENV LD_LIBRARY_PATH=/usr/local/lib:/usr/local/libtorch/lib:$LD_LIBRARY_PATH
ENV PATH=/usr/local/bin:$PATH

# Expose port for potential web interface
EXPOSE 8080

# Default command - run comprehensive tests
CMD ["/workspace/comprehensive-test.sh"]