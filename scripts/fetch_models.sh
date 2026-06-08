#!/usr/bin/env bash
# Download Pix2Text models from hf-mirror (China-friendly fallback)
set -euo pipefail

MIRROR="https://hf-mirror.com"
DEST="${HOME}/.pix2text/1.1"
mkdir -p "$DEST"

echo "[fetch] downloading models to $DEST ..."

# MFD (formula detection)
mkdir -p "$DEST/mfd-1.5-onnx"
curl -sL --retry 3 \
  "${MIRROR}/breezedeus/pix2text-mfd/resolve/main/pix2text-mfd-1.5.onnx" \
  -o "$DEST/mfd-1.5-onnx/pix2text-mfd-1.5.onnx"
curl -sL --retry 3 \
  "${MIRROR}/breezedeus/pix2text-mfd/resolve/main/config.yaml" \
  -o "$DEST/mfd-1.5-onnx/config.yaml"

# Layout (DocLayout-YOLO)
mkdir -p "$DEST/layout-docyolo"
curl -sL --retry 3 \
  "${MIRROR}/breezedeus/pix2text-layout/resolve/main/doclayout_yolo_docstructbench_imgsz1024.pt" \
  -o "$DEST/layout-docyolo/doclayout_yolo_docstructbench_imgsz1024.pt"
curl -sL --retry 3 \
  "${MIRROR}/breezedeus/pix2text-layout/resolve/main/config.yaml" \
  -o "$DEST/layout-docyolo/config.yaml"

# MFR (formula recognition) — encoder + decoder + tokenizer
mkdir -p "$DEST/mfr-1.5-onnx"
curl -sL --retry 3 \
  "${MIRROR}/breezedeus/pix2text-mfr/resolve/main/encoder_model.onnx" \
  -o "$DEST/mfr-1.5-onnx/encoder_model.onnx"
curl -sL --retry 3 \
  "${MIRROR}/breezedeus/pix2text-mfr/resolve/main/decoder_model.onnx" \
  -o "$DEST/mfr-1.5-onnx/decoder_model.onnx"
for f in config.json tokenizer_config.json vocab.json merges.txt special_tokens_map.json preprocessor_config.json; do
  curl -sL --retry 3 \
    "${MIRROR}/breezedeus/pix2text-mfr/resolve/main/${f}" \
    -o "$DEST/mfr-1.5-onnx/${f}" || true
done

echo "[fetch] done. total size:"
du -sh "$DEST"
