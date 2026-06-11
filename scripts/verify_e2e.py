"""End-to-end OCR verification on samples/synthetic_math.png."""
from server.engines.local import LocalEngine

eng = LocalEngine(device="cpu", enable_table=False)
r = eng.recognize("samples/synthetic_math.png")
print("engine:", r.engine, "| elapsed:", f"{r.elapsed_s:.2f}s")
print("---")
print(r.text)
