"""Read-only: dump Pix2Text's model catalog so we can manually download."""
from pix2text.consts import AVAILABLE_MODELS
import json

# Pix2Text 的 AVAILABLE_MODELS 是 ModelInfos 类，遍历内部 dict
inner = getattr(AVAILABLE_MODELS, "_models", None) or AVAILABLE_MODELS.__dict__
print("type:", type(AVAILABLE_MODELS).__name__)
print("attrs:", [a for a in dir(AVAILABLE_MODELS) if not a.startswith("_")][:20])
# 试几种常见的查询
for name in ("mfd-1.5", "layout"):
    for backend in ("onnx", "pytorch"):
        try:
            info = AVAILABLE_MODELS.get_info(name, backend)
            print(f"--- {name} / {backend} ---")
            print(json.dumps(info, indent=2, default=str)[:600])
        except Exception as e:
            print(f"--- {name} / {backend}: {e}")
