# PROTOTYPE — throwaway FastAPI single-file web UI for FIT-OCR
# Per prototype skill rules:
#   - No tests, no error handling beyond runnability
#   - Loud STATE prints on every action
#   - Single file, hard-coded paths OK
#   - Goal: prove end-to-end loop {photo upload → Pix2Text → Markdown+LaTeX → browser}
#
# Three-pane UI (per Q4 decision):
#   left:    original image
#   center:  KaTeX rendered output
#   right:   raw LaTeX/Markdown source (editable)
#
# Crop-rerun is NOT in this prototype — that's a v2 feature once basics work.
#
# Run:
#   cd prototype && source .venv/bin/activate
#   uvicorn web_proto:app --host 0.0.0.0 --port 8001 --reload
# Then visit:
#   http://localhost:8001          on this machine
#   http://100.123.57.69:8001      from phone via Tailscale
from __future__ import annotations

import io
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

PROTO_DIR = Path(__file__).parent
UPLOAD_DIR = PROTO_DIR / "uploads"
OUTPUT_DIR = PROTO_DIR / "output"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="FIT-OCR Prototype")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")


# Lazy global: load Pix2Text once on first request, keep in memory.
# Bad pattern for prod, fine for prototype.
_P2T = None


def _get_p2t():
    global _P2T
    if _P2T is None:
        print("\n[STATE] Loading Pix2Text (first request) ...")
        t0 = time.time()
        from pix2text import Pix2Text
        _P2T = Pix2Text.from_config(device="cpu", enable_table=False)
        print(f"[STATE] Pix2Text loaded in {time.time()-t0:.1f}s")
    return _P2T


INDEX_HTML = """<!doctype html>
<html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FIT-OCR Prototype</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<style>
  body{margin:0;font-family:-apple-system,sans-serif;background:#111;color:#eee}
  header{padding:1rem;background:#222;display:flex;gap:1rem;align-items:center;flex-wrap:wrap}
  header h1{margin:0;font-size:1.1rem}
  .panes{display:grid;grid-template-columns:1fr 1fr 1fr;gap:.5rem;padding:.5rem;height:calc(100vh - 80px)}
  .pane{background:#1a1a1a;border:1px solid #333;border-radius:6px;overflow:auto;padding:.75rem;min-height:0}
  .pane h2{font-size:.85rem;margin:0 0 .5rem;color:#888;text-transform:uppercase;letter-spacing:.05em}
  img.preview{max-width:100%;height:auto;display:block;background:#000}
  textarea{width:100%;height:calc(100% - 2rem);background:#0d0d0d;color:#9f9;border:none;font:13px/1.5 monospace;resize:none;padding:.5rem;box-sizing:border-box}
  #rendered{font-size:1rem;line-height:1.6}
  #rendered .katex-display{margin:.5em 0}
  button,label.btn{background:#3a7;color:#fff;padding:.5rem 1rem;border:0;border-radius:4px;cursor:pointer;font-weight:600}
  label.btn input{display:none}
  #status{color:#ff8;font-size:.9rem}
  @media(max-width:768px){.panes{grid-template-columns:1fr;grid-template-rows:1fr 1fr 1fr;height:auto}.pane{height:60vh}}
</style></head><body>
<header>
  <h1>📐 FIT-OCR Prototype</h1>
  <label class="btn">📷 拍照/选图<input type="file" id="file" accept="image/*" capture="environment"></label>
  <button id="go" disabled>识别</button>
  <span id="status">等待选图</span>
</header>
<div class="panes">
  <div class="pane"><h2>原图</h2><img id="img" class="preview"></div>
  <div class="pane"><h2>渲染</h2><div id="rendered">尚无结果</div></div>
  <div class="pane"><h2>LaTeX 源码</h2><textarea id="src" placeholder="识别结果将在这里显示，可编辑"></textarea></div>
</div>
<script>
const $file = document.getElementById('file');
const $img  = document.getElementById('img');
const $go   = document.getElementById('go');
const $stat = document.getElementById('status');
const $src  = document.getElementById('src');
const $ren  = document.getElementById('rendered');
let currentFile = null;

$file.addEventListener('change', e => {
  const f = e.target.files[0]; if (!f) return;
  currentFile = f;
  $img.src = URL.createObjectURL(f);
  $stat.textContent = f.name + ' (' + (f.size/1024).toFixed(0) + ' KB)';
  $go.disabled = false;
});

$go.addEventListener('click', async () => {
  if (!currentFile) return;
  $go.disabled = true;
  $stat.textContent = '识别中…可能需要 5-30 秒';
  const fd = new FormData(); fd.append('file', currentFile);
  const t0 = performance.now();
  const r = await fetch('/recognize', {method:'POST', body:fd});
  const j = await r.json();
  const t  = ((performance.now()-t0)/1000).toFixed(1);
  if (!r.ok) { $stat.textContent = '错误: ' + (j.detail||j.error); $go.disabled = false; return; }
  $stat.textContent = `识别完成 ${t}s · 输出 ${j.markdown.length} 字符`;
  $src.value = j.markdown;
  renderMarkdown(j.markdown);
  $go.disabled = false;
});

$src.addEventListener('input', () => renderMarkdown($src.value));

function renderMarkdown(md){
  // very dumb markdown→html: paragraphs, line breaks, $$..$$ blocks, $..$ inline
  let html = md
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\\n\\n+/g,'</p><p>')
    .replace(/\\n/g,'<br>');
  $ren.innerHTML = '<p>'+html+'</p>';
  if (window.renderMathInElement) renderMathInElement($ren, {
    delimiters:[
      {left:'$$',right:'$$',display:true},
      {left:'$',right:'$',display:false},
      {left:'\\\\(',right:'\\\\)',display:false},
      {left:'\\\\[',right:'\\\\]',display:true},
    ],
    throwOnError:false
  });
}
</script>
</body></html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML


@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    print(f"\n[STATE] /recognize ← {file.filename} ({file.content_type})")
    data = await file.read()
    ext = (Path(file.filename or "img.png").suffix or ".png").lower()
    name = f"{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"
    img_path = UPLOAD_DIR / name
    img_path.write_bytes(data)
    print(f"[STATE] saved {img_path} ({len(data)} bytes)")

    try:
        p2t = _get_p2t()
        t0 = time.time()
        # Lightweight: skip layout analysis, direct OCR
        md = p2t.recognize(str(img_path), file_type="text")
        elapsed = time.time() - t0
        out_md = OUTPUT_DIR / (img_path.stem + ".md")
        out_md.write_text(md, encoding="utf-8")
        print(f"[STATE] OCR ok in {elapsed:.1f}s, {len(md)} chars → {out_md}")
        return JSONResponse({
            "image_url": f"/uploads/{name}",
            "markdown_url": f"/output/{out_md.name}",
            "markdown": md,
            "elapsed_s": elapsed,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/health")
def health():
    import torch
    return {
        "ok": True,
        "torch": torch.__version__,
        "cuda": torch.cuda.is_available(),
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "p2t_loaded": _P2T is not None,
    }
