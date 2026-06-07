#!/usr/bin/env bash
# Manually fetch Pix2Text model weights bypassing huggingface_hub Python client.
# Reason: hf_hub causes connection stalls via Clash proxy; plain curl is stable.
# Writes to ~/.pix2text/1.1/{mfd-1.5-onnx, layout-docyolo, mfr-1.5}/
set -u
PROXY="http://127.0.0.1:7897"
BASE="https://hf-mirror.com"
ROOT="$HOME/.pix2text/1.1"
mkdir -p "$ROOT/mfd-1.5-onnx" "$ROOT/layout-docyolo" "$ROOT/mfr-1.5"

fetch() {
  local url="$1" out="$2" label="$3"
  echo "[fetch] $label  →  $out"
  time curl -sL -x "$PROXY" -o "$out" \
    -w "  done http=%{http_code} size=%{size_download}B speed=%{speed_download}B/s time=%{time_total}s\n" \
    "$url"
}

# Big binaries
fetch "$BASE/breezedeus/pix2text-mfd-1.5/resolve/main/pix2text-mfd-1.5.onnx" \
      "$ROOT/mfd-1.5-onnx/pix2text-mfd-1.5.onnx" "mfd onnx (80M)"
fetch "$BASE/breezedeus/pix2text-layout-docyolo/resolve/main/doclayout_yolo_docstructbench_imgsz1024.pt" \
      "$ROOT/layout-docyolo/doclayout_yolo_docstructbench_imgsz1024.pt" "layout pt (41M)"
fetch "$BASE/breezedeus/pix2text-mfr-1.5/resolve/main/encoder_model.onnx" \
      "$ROOT/mfr-1.5/encoder_model.onnx" "mfr encoder (88M)"
fetch "$BASE/breezedeus/pix2text-mfr-1.5/resolve/main/decoder_model.onnx" \
      "$ROOT/mfr-1.5/decoder_model.onnx" "mfr decoder (32M)"

# Small files
for f in config.json generation_config.json preprocessor_config.json \
         special_tokens_map.json tokenizer.json tokenizer_config.json; do
  fetch "$BASE/breezedeus/pix2text-mfr-1.5/resolve/main/$f" \
        "$ROOT/mfr-1.5/$f" "mfr/$f"
done
fetch "$BASE/breezedeus/pix2text-mfd-1.5/resolve/main/config.yaml" \
      "$ROOT/mfd-1.5-onnx/config.yaml" "mfd/config.yaml"
fetch "$BASE/breezedeus/pix2text-layout-docyolo/resolve/main/config.yaml" \
      "$ROOT/layout-docyolo/config.yaml" "layout/config.yaml"

echo
echo "=== final sizes ==="
du -sh "$ROOT"/*/
echo
echo "=== files ==="
find "$ROOT" -type f -printf "%s %p\n" | sort -nr
