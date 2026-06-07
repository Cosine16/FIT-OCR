"""
PROTOTYPE — throwaway smoke test for FIT-OCR.

Question this answers:
  Can Pix2Text + UniMERNet load on this 4GB GTX 1650 + WSL2 setup,
  and produce reasonable LaTeX output on a real math note photo?

Usage:
    python smoke_test.py path/to/image.jpg
    python smoke_test.py             # uses samples/*.jpg if any

Per prototype skill: no error handling beyond runnability,
no tests, results dumped to stdout + output/ for human inspection.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROTO_DIR = Path(__file__).parent
OUTPUT_DIR = PROTO_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def print_state(label: str, data) -> None:
    """Per prototype skill rule 5: surface state after every action."""
    print(f"\n{'=' * 60}\n[STATE] {label}\n{'=' * 60}")
    if isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str)[:2000])
    else:
        print(str(data)[:2000])


def check_torch():
    import torch
    info = {
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_count": torch.cuda.device_count(),
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "device_capability": torch.cuda.get_device_capability(0) if torch.cuda.is_available() else None,
        "mem_total_gb": (torch.cuda.get_device_properties(0).total_memory / 1024**3) if torch.cuda.is_available() else None,
    }
    print_state("PyTorch / CUDA", info)
    return info["cuda_available"]


def try_pix2text(image_path: Path, use_cuda: bool):
    from pix2text import Pix2Text  # noqa: WPS433 — prototype, lazy import on purpose
    device = "cuda" if use_cuda else "cpu"
    print(f"\n[pix2text] loading on device={device} ...")
    t0 = time.time()
    p2t = Pix2Text.from_config(device=device)
    print(f"[pix2text] loaded in {time.time() - t0:.1f}s")

    print(f"[pix2text] recognizing {image_path.name} ...")
    t0 = time.time()
    md = p2t.recognize(str(image_path), file_type="page", return_text=True)
    elapsed = time.time() - t0
    print_state(f"Pix2Text output ({elapsed:.1f}s)", md)

    out = OUTPUT_DIR / f"{image_path.stem}.pix2text.md"
    out.write_text(md, encoding="utf-8")
    print(f"[pix2text] saved → {out}")
    return md


def try_unimernet(image_path: Path, use_cuda: bool):
    """Optional — UniMERNet for a cropped single formula."""
    try:
        import unimernet  # noqa: F401
    except ImportError:
        print("\n[unimernet] not installed yet — skipping. install with:")
        print("    uv pip install unimernet")
        return None
    # UniMERNet API stub — actual call shape depends on installed version
    print("\n[unimernet] (placeholder — wire up after install)")
    return None


def main():
    args = sys.argv[1:]
    if args:
        images = [Path(a) for a in args]
    else:
        samples = PROTO_DIR / "samples"
        images = sorted(samples.glob("*.jpg")) + sorted(samples.glob("*.png"))
        if not images:
            print("No image given and no samples/*.jpg|png found.")
            print("Usage: python smoke_test.py path/to/photo.jpg")
            print(f"Or drop test images into: {samples}")
            sys.exit(1)

    use_cuda = check_torch()

    for img in images:
        if not img.exists():
            print(f"[skip] {img} not found")
            continue
        print(f"\n{'#' * 60}\n# IMAGE: {img}\n{'#' * 60}")
        try_pix2text(img, use_cuda)
        try_unimernet(img, use_cuda)


if __name__ == "__main__":
    main()
