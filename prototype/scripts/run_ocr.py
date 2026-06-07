"""Run OCR on an image and show results with resource usage."""
from pathlib import Path
import time
import sys

img_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "samples" / "synthetic_math.png"

print(f"[OCR] image: {img_path}")
print(f"[OCR] size: {img_path.stat().st_size / 1024:.0f} KB")

from pix2text import Pix2Text

print("[OCR] loading model (cpu, no table)...")
t0 = time.time()
p2t = Pix2Text.from_config(device="cpu", enable_table=False)
print(f"[OCR] loaded in {time.time()-t0:.1f}s")

print("[OCR] recognizing with file_type='text' (lightweight)...")
t0 = time.time()
page = p2t.recognize(str(img_path), file_type="text")
elapsed = time.time() - t0

if isinstance(page, str):
    md = page
else:
    lines = [el.text for el in page.elements]
    md = "\n\n".join(lines)

print(f"\n{'='*50}")
print(f"RESULT ({len(md)} chars, {elapsed:.1f}s)")
print(f"{'='*50}")
print(md)
print(f"{'='*50}")
