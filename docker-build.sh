#!/bin/bash

# Docker build helper script for YOLO Torch
# Usage: ./docker-build.sh [gpu|cpu] [tag]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BUILD_TYPE=${1:-gpu}
TAG=${2:-yolo-torch}

echo -e "${GREEN}YOLO Torch Docker Build Script${NC}"
echo "=================================="
echo "Build Type: $BUILD_TYPE"
echo "Image Tag: $TAG"
echo ""

if [ "$BUILD_TYPE" = "cpu" ]; then
    echo -e "${YELLOW}Building CPU-only image...${NC}"
    docker build -t "$TAG" \
        --build-arg CUDA_VERSION=cpu \
        -f Dockerfile \
        .
elif [ "$BUILD_TYPE" = "gpu" ]; then
    echo -e "${YELLOW}Building GPU-enabled image...${NC}"
    docker build -t "$TAG" \
        --build-arg CUDA_VERSION=12.1 \
        -f Dockerfile \
        .
else
    echo -e "${RED}Error: Invalid build type. Use 'gpu' or 'cpu'${NC}"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image built successfully: $TAG${NC}"
    echo ""
    echo "Usage:"
    if [ "$BUILD_TYPE" = "gpu" ]; then
        echo "  docker run --gpus all -v \$(pwd):/workspace $TAG yolo-stock model.torchscript image.jpg"
    else
        echo "  docker run -v \$(pwd):/workspace $TAG yolo-stock model.torchscript image.jpg"
    fi
else
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
fi