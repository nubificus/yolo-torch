cmake_minimum_required(VERSION 3.18)
project(yolo-torch VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Release)

# Find CUDA
find_package(CUDA QUIET)
if(CUDA_FOUND)
    enable_language(CUDA)
    message(STATUS "CUDA found: ${CUDA_VERSION}")
    set(CUDA_AVAILABLE TRUE)
else()
    message(STATUS "CUDA not found - building CPU only")
    set(CUDA_AVAILABLE FALSE)
endif()

# Find LibTorch using Python torch location
set(LIBTORCH_PATH "/usr/local/lib/python3.10/dist-packages/torch")
if(DEFINED LIBTORCH_ROOT)
    set(LIBTORCH_PATH ${LIBTORCH_ROOT})
endif()

message(STATUS "Using LibTorch from: ${LIBTORCH_PATH}")

# Set LibTorch paths for CMake
set(CMAKE_PREFIX_PATH "${CMAKE_PREFIX_PATH};${LIBTORCH_PATH}")
find_package(Torch REQUIRED)

if(CUDA_AVAILABLE)
    # Try to find CUDA components
    find_library(TORCH_CUDA_LIB torch_cuda PATHS ${LIBTORCH_PATH}/lib NO_DEFAULT_PATH)
    if(TORCH_CUDA_LIB)
        message(STATUS "Found CUDA-enabled LibTorch")
        set(HAS_TORCH_CUDA TRUE)
    else()
        message(STATUS "LibTorch CUDA not found, using CPU version")
        set(HAS_TORCH_CUDA FALSE)
    endif()
endif()

# Find OpenCV
find_package(OpenCV REQUIRED COMPONENTS core imgproc imgcodecs)
message(STATUS "OpenCV found: ${OpenCV_VERSION}")

# Set compilation flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_GLIBCXX_USE_CXX11_ABI=1")
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -DNDEBUG")
endif()

# Include directories
include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(${TORCH_INCLUDE_DIRS})

# Stock example
add_executable(yolo-stock yolo-stock.cc)
target_link_libraries(yolo-stock "${TORCH_LIBRARIES}")
target_link_libraries(yolo-stock ${OpenCV_LIBS})

if(CUDA_AVAILABLE AND HAS_TORCH_CUDA)
    target_link_libraries(yolo-stock torch_cuda)
    target_link_libraries(yolo-stock c10_cuda)
endif()

# Set properties
set_property(TARGET yolo-stock PROPERTY CXX_STANDARD 17)
set_property(TARGET yolo-stock PROPERTY POSITION_INDEPENDENT_CODE ON)

# Simple example
add_executable(yolo-simple yolo-simple.cc)
target_link_libraries(yolo-simple "${TORCH_LIBRARIES}")
target_link_libraries(yolo-simple ${OpenCV_LIBS})

if(CUDA_AVAILABLE AND HAS_TORCH_CUDA)
    target_link_libraries(yolo-simple torch_cuda)
    target_link_libraries(yolo-simple c10_cuda)
endif()

# Set properties
set_property(TARGET yolo-simple PROPERTY CXX_STANDARD 17)
set_property(TARGET yolo-simple PROPERTY POSITION_INDEPENDENT_CODE ON)

# vAccel example (optional)
find_library(VACCEL_LIB vaccel)
if(VACCEL_LIB)
    message(STATUS "vAccel found, building yolo-vaccel")
    add_executable(yolo-vaccel yolo-vaccel.cc)
    target_link_libraries(yolo-vaccel "${TORCH_LIBRARIES}")
    target_link_libraries(yolo-vaccel ${OpenCV_LIBS})
    target_link_libraries(yolo-vaccel ${VACCEL_LIB})
    
    if(CUDA_AVAILABLE AND HAS_TORCH_CUDA)
        target_link_libraries(yolo-vaccel torch_cuda)
        target_link_libraries(yolo-vaccel c10_cuda)
    endif()
    
    set_property(TARGET yolo-vaccel PROPERTY CXX_STANDARD 17)
    set_property(TARGET yolo-vaccel PROPERTY POSITION_INDEPENDENT_CODE ON)
else()
    message(STATUS "vAccel library not found - skipping vAccel example")
endif()

# Installation
install(TARGETS yolo-stock DESTINATION bin)
if(VACCEL_LIB)
    install(TARGETS yolo-vaccel DESTINATION bin)
endif()

# Print build configuration
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ flags: ${CMAKE_CXX_FLAGS}")
if(CUDA_AVAILABLE)
    message(STATUS "CUDA enabled: YES")
else()
    message(STATUS "CUDA enabled: NO")
endif()