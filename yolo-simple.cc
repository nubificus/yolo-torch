#include <iostream>
#include <vector>
#include <string>
#include <opencv2/opencv.hpp>
#include <torch/torch.h>
#include <torch/script.h>

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <model_path> <image_path>" << std::endl;
        return 1;
    }

    try {
        // Set device
        torch::Device device(torch::cuda::is_available() ? torch::kCUDA : torch::kCPU);
        std::cout << "Using device: " << (device.is_cuda() ? "CUDA" : "CPU") << std::endl;

        // Load model
        std::string model_path = argv[1];
        torch::jit::script::Module model = torch::jit::load(model_path);
        model.eval();
        model.to(device);
        std::cout << "Model loaded successfully" << std::endl;

        // Load and preprocess image
        cv::Mat image = cv::imread(argv[2]);
        if (image.empty()) {
            std::cerr << "Failed to load image: " << argv[2] << std::endl;
            return 1;
        }

        // Convert to tensor
        cv::Mat resized_image;
        cv::resize(image, resized_image, cv::Size(640, 640));
        
        // Convert BGR to RGB
        cv::Mat rgb_image;
        cv::cvtColor(resized_image, rgb_image, cv::COLOR_BGR2RGB);
        
        // Create tensor
        auto tensor = torch::from_blob(
            rgb_image.data, 
            {1, rgb_image.rows, rgb_image.cols, 3}, 
            torch::kByte
        );
        
        // Convert to float and normalize
        tensor = tensor.to(torch::kFloat32) / 255.0;
        
        // Permute dimensions: [1, H, W, C] -> [1, C, H, W]
        tensor = tensor.permute({0, 3, 1, 2});
        
        // Move to device
        tensor = tensor.to(device);

        // Create input vector
        std::vector<torch::jit::IValue> inputs;
        inputs.push_back(tensor);

        // Run inference
        std::cout << "Running inference..." << std::endl;
        torch::Tensor output = model.forward(inputs).toTensor();
        
        // Move output to CPU for processing
        output = output.cpu();
        
        std::cout << "Inference completed successfully" << std::endl;
        std::cout << "Output shape: [" << output.size(0) << ", " << output.size(1) << "]" << std::endl;
        
        // Simple detection: look for high confidence scores (assuming YOLO format)
        if (output.size(1) > 4) {
            auto scores = output.slice(1, 4, 5);  // Get confidence scores
            auto max_score = scores.max().item<float>();
            std::cout << "Max confidence score: " << max_score << std::endl;
            
            // Count detections above threshold
            int detections = 0;
            auto confidence_threshold = 0.5f;
            
            for (int i = 0; i < output.size(0); i++) {
                auto conf = output[i][4].item<float>();
                if (conf > confidence_threshold) {
                    detections++;
                }
            }
            std::cout << "Objects detected with confidence > " << confidence_threshold << ": " << detections << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}