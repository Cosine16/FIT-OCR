"""Verify PyTorch + CUDA + GTX 1650 actually work. Pure read-only test."""
import time
import torch

print("torch:", torch.__version__)
print("cuda compiled:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
    print("capability:", torch.cuda.get_device_capability(0))
    print("mem GB:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2))
    a = torch.randn(512, 512, device="cuda")
    b = torch.randn(512, 512, device="cuda")
    t = time.time()
    for _ in range(100):
        c = a @ b
    torch.cuda.synchronize()
    print(f"100x 512x512 matmul: {(time.time()-t)*1000:.1f}ms")
    print("matmul sum:", round(c.sum().item(), 2))
else:
    print("FAIL — torch can't see GPU, would need to fall back to CPU")
