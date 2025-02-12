cmake_minimum_required(VERSION 3.0)
project(YOLO)

set(CMAKE_CXX_STANDARD 17)

find_package(Torch REQUIRED)
find_package(OpenCV REQUIRED)

# Stock example
add_executable(yolo-stock yolo-stock.cc)
target_link_libraries(yolo-stock "${TORCH_LIBRARIES}")
target_link_libraries(yolo-stock ${OpenCV_LIBS})

# vAccel example
add_executable(yolo-vaccel yolo-vaccel.cc)
target_link_libraries(yolo-vaccel "${TORCH_LIBRARIES}")
target_link_libraries(yolo-vaccel ${OpenCV_LIBS})
target_link_libraries(yolo-vaccel vaccel)

set_property(TARGET yolo-stock PROPERTY CXX_STANDARD 17)
set_property(TARGET yolo-vaccel PROPERTY CXX_STANDARD 17)
