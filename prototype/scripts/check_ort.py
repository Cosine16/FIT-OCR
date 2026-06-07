"""Check onnxruntime providers for GPU support."""
import onnxruntime as ort
print("onnxruntime:", ort.__version__)
print("available providers:", ort.get_available_providers())