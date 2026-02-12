#!/bin/bash

# Build script for YOLO Torch project with GPU support
# Usage: ./build.sh [clean]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}YOLO Torch Build Script${NC}"
echo "==============================="

# Clean build if requested
if [ "$1" = "clean" ]; then
    echo -e "${YELLOW}Cleaning build directory...${NC}"
    rm -rf build
    echo -e "${GREEN}Clean completed.${NC}"
    exit 0
fi

# Check if CUDA is available
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -c2-)
    echo -e "${GREEN}CUDA found: $CUDA_VERSION${NC}"
    CUDA_AVAILABLE=true
else
    echo -e "${YELLOW}CUDA not found - building CPU only version${NC}"
    CUDA_AVAILABLE=false
fi

# Create build directory
mkdir -p build
cd build

# Configure with CMake
echo -e "${YELLOW}Configuring with CMake...${NC}"

CMAKE_ARGS=(
    "-DCMAKE_BUILD_TYPE=Release"
    "-DCMAKE_PREFIX_PATH=/opt/libtorch"
)

if [ "$CUDA_AVAILABLE" = true ]; then
    CMAKE_ARGS+=("-DCMAKE_CUDA_ARCHITECTURES=all")
    echo -e "${GREEN}Building with CUDA support${NC}"
else
    echo -e "${YELLOW}Building CPU only version${NC}"
fi

cmake .. "${CMAKE_ARGS[@]}"

# Build
echo -e "${YELLOW}Building...${NC}"
make -j$(nproc)

# Check if build was successful
if [ -f "yolo-stock" ]; then
    echo -e "${GREEN}✓ yolo-stock built successfully${NC}"
else
    echo -e "${RED}✗ yolo-stock build failed${NC}"
    exit 1
fi

if [ -f "yolo-vaccel" ]; then
    echo -e "${GREEN}✓ yolo-vaccel built successfully${NC}"
else
    echo -e "${YELLOW}⚠ yolo-vaccel not built (vAccel library not found)${NC}"
fi

echo -e "${GREEN}Build completed successfully!${NC}"
echo ""
echo "Usage:"
echo "  ./yolo-stock <model_path> <image_path>"
if [ -f "yolo-vaccel" ]; then
    echo "  ./yolo-vaccel <model_path> <image_path>"
fi

cd ..