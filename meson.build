project('yolo-torch', 'cpp',
  version : '1.0.0',
  default_options : [
    'warning_level=3',
    'cpp_std=c++17',
    'buildtype=release'
  ]
)

# Find dependencies
cuda_dep = dependency('cuda', required: false)
if not cuda_dep.found()
  warning('CUDA not found, building CPU-only version')
  cuda_available = false
else
  message('CUDA found, building with GPU support')
  cuda_available = true
endif

# Find OpenCV using pkg-config
opencv_dep = dependency('opencv4', required: false)
if not opencv_dep.found()
  opencv_dep = dependency('opencv', required: true)
endif

# Find LibTorch - use Python torch location
libtorch_path = get_option('libtorch_path')
if libtorch_path == ''
  # Default to Python torch location
  libtorch_path = '/usr/local/lib/python3.10/dist-packages/torch'
endif

message('Using LibTorch from: ' + libtorch_path)

# LibTorch dependencies
libtorch_include = include_directories(libtorch_path + '/include')
libtorch_libdir = libtorch_path + '/lib'

# LibTorch libraries
libtorch_libs = [
  'torch_cpu',
  'c10',
  'gloo'
]

if cuda_available
  libtorch_libs += ['torch_cuda', 'c10_cuda']
endif

# Filter out empty strings and create dependencies
libtorch_deps = []
foreach lib : libtorch_libs
  libtorch_deps += cc.find_library(lib, dirs: libtorch_libdir, required: true)
endforeach

# Thread dependency
threads_dep = dependency('threads')

# Executables
executable('yolo-stock',
  'yolo-stock.cc',
  include_directories: libtorch_include,
  dependencies: [opencv_dep, threads_dep] + libtorch_deps,
  cpp_args: ['-D_GLIBCXX_USE_CXX11_ABI=1'],
  install: true,
  install_dir: get_option('bindir')
)

# Build yolo-vaccel if vaccel support is requested
vaccel_dep = dependency('vaccelrt', required: false)
if vaccel_dep.found()
  executable('yolo-vaccel',
    'yolo-vaccel.cc',
    include_directories: libtorch_include,
    dependencies: [opencv_dep, threads_dep, vaccel_dep] + libtorch_deps,
    cpp_args: ['-D_GLIBCXX_USE_CXX11_ABI=1'],
    install: true,
    install_dir: get_option('bindir')
  )
endif