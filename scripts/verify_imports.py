"""Light import verification — no model loading."""
import sys

print("Python:", sys.version.split()[0])
print()

checks = [
    ("fit_ocr", "fit_ocr"),
    ("fit_ocr.core.models", "fit_ocr.core.models"),
    ("fit_ocr.core.interfaces", "fit_ocr.core.interfaces"),
    ("fit_ocr.core.exceptions", "fit_ocr.core.exceptions"),
    ("fit_ocr.engines.local", "fit_ocr.engines.local"),
    ("fit_ocr.engines.cloud", "fit_ocr.engines.cloud"),
    ("fit_ocr.engines.fallback", "fit_ocr.engines.fallback"),
    ("fit_ocr.infrastructure.config", "fit_ocr.infrastructure.config"),
    ("fit_ocr.web.app", "fit_ocr.web.app"),
    ("pix2text", "pix2text"),
    ("torch", "torch"),
    ("fastapi", "fastapi"),
    ("zhipuai", "zhipuai"),
]

ok = 0
fail = 0
for name, mod in checks:
    try:
        __import__(mod)
        print(f"  ok  {name}")
        ok += 1
    except Exception as e:
        print(f"  FAIL  {name}: {type(e).__name__}: {e}")
        fail += 1

print()
print(f"Result: {ok} ok, {fail} fail")
sys.exit(0 if fail == 0 else 1)
