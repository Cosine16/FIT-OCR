"""Check installed package versions."""
import importlib
for pkg in ['optimum', 'onnxruntime', 'transformers', 'torch']:
    try:
        mod = importlib.import_module(pkg)
        print(f"{pkg}: {mod.__version__}")
    except Exception as e:
        print(f"{pkg}: error {e}")
