cmake_minimum_required(VERSION 3.0)
project(YOLOv8Inference)

set(CMAKE_CXX_STANDARD 17)

# Add LibTorch
find_package(Torch REQUIRED)
find_package(OpenCV REQUIRED)

add_executable(YOLOv8Inference main.cpp)

target_link_libraries(YOLOv8Inference "${TORCH_LIBRARIES}")
target_link_libraries(YOLOv8Inference ${OpenCV_LIBS})

set_property(TARGET YOLOv8Inference PROPERTY CXX_STANDARD 17)
