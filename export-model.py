import torch
import torch.nn as nn

# Create a simple test model that works with TorchScript
class SimpleYOLO(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 64, 7, stride=2, padding=3)
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(64, 10)  # 10 classes for simplicity
        
    def forward(self, x):
        x = self.conv(x)
        x = torch.relu(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

# Create and export model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SimpleYOLO()
model.eval()
model.to(device)

# Create dummy input
dummy_input = torch.randn(1, 3, 640, 640, device=device)

# Export to TorchScript
scripted_model = torch.jit.script(model)
scripted_model.save("simple-yolo.pt")

print(f"Model exported to simple-yolo.pt on device: {device}")
print(f"Model input shape: {dummy_input.shape}")
print(f"Model output shape: {model(dummy_input).shape}")