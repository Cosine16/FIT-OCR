"""FastAPI application factory."""
from __future__ import annotations

import time
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from server.infrastructure.config import Config
from server.infrastructure.logging import setup_logging
from server.infrastructure.database import init_db, get_session
from server.infrastructure.models import OCRRecord, RecordStatus
from server.engines.local import LocalEngine
from server.engines.cloud import CloudEngine
from server.engines.fallback import FallbackEngine
from server.api.routes.admin import router as admin_router


def create_app(config: Config | None = None) -> FastAPI:
    """Application factory — creates and configures FastAPI app."""
    cfg = config or Config.from_env()
    setup_logging(cfg.log_level)

    # Initialize database
    init_db()

    app = FastAPI(title="FIT-OCR")

    # Ensure data dirs exist
    cfg.upload_dir.mkdir(parents=True, exist_ok=True)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    # Admin panel static mount (populated by web-admin build)
    admin_static = Path(__file__).parent / "static" / "admin"
    if not admin_static.exists():
        admin_static.mkdir(parents=True, exist_ok=True)

    # Static mounts — MUST be before router registration
    app.mount("/uploads", StaticFiles(directory=str(cfg.upload_dir)), name="uploads")
    app.mount("/output", StaticFiles(directory=str(cfg.output_dir)), name="output")

    # Admin panel SPA (built by web-admin)
    app.mount("/admin", StaticFiles(directory=str(admin_static), html=True), name="admin")

    # Register admin API router
    app.include_router(admin_router)

    # Engine registry
    _engines: dict[str, object] = {}

    def _get_engine(mode: str):
        if mode not in _engines:
            if mode == "local":
                _engines[mode] = LocalEngine(device=cfg.device, enable_table=cfg.enable_table)
            elif mode == "cloud":
                _engines[mode] = CloudEngine(api_key=cfg.zhipu_api_key, model=cfg.cloud_model)
            else:
                local = LocalEngine(device=cfg.device, enable_table=cfg.enable_table)
                cloud = CloudEngine(api_key=cfg.zhipu_api_key, model=cfg.cloud_model)
                _engines[mode] = FallbackEngine(local=local, cloud=cloud)
        return _engines[mode]

    @app.get("/", response_class=HTMLResponse)
    def index():
        return _load_index_html()

    @app.post("/recognize")
    async def recognize(file: UploadFile = File(...), engine: str = Form("fallback")):
        data = await file.read()
        ext = (Path(file.filename or "img.png").suffix or ".png").lower()
        name = f"{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"
        img_path = cfg.upload_dir / name
        img_path.write_bytes(data)

        t0 = time.time()
        eng = _get_engine(engine)
        try:
            result = eng.recognize(img_path)
            out_md = cfg.output_dir / (img_path.stem + ".md")
            out_md.write_text(result.text, encoding="utf-8")

            # Save record to DB
            _save_record(
                image_filename=name,
                engine=result.engine,
                status=RecordStatus.SUCCESS,
                result_path=str(out_md),
                result_preview=result.text[:500],
                elapsed_s=result.elapsed_s,
                image_size_bytes=len(data),
            )

            return JSONResponse({
                "image_url": f"/uploads/{name}",
                "markdown_url": f"/output/{out_md.name}",
                "markdown": result.text,
                "elapsed_s": round(result.elapsed_s, 2),
                "engine": result.engine,
            })
        except Exception as exc:
            elapsed = time.time() - t0
            _save_record(
                image_filename=name,
                engine=engine,
                status=RecordStatus.FAILURE,
                elapsed_s=elapsed,
                image_size_bytes=len(data),
                error_msg=str(exc),
            )
            raise

    @app.get("/health")
    def health():
        import torch
        return {
            "ok": True,
            "torch": torch.__version__,
            "cuda": torch.cuda.is_available(),
            "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        }

    return app


def _save_record(
    image_filename: str,
    engine: str,
    status: RecordStatus,
    elapsed_s: float = 0.0,
    result_path: str | None = None,
    result_preview: str | None = None,
    image_size_bytes: int = 0,
    error_msg: str | None = None,
):
    """Persist an OCR call to the database."""
    try:
        db = get_session()
        record = OCRRecord(
            image_filename=image_filename,
            engine=engine,
            status=status,
            result_path=result_path,
            result_text_preview=result_preview,
            elapsed_ms=round(elapsed_s * 1000, 1),
            image_size_bytes=image_size_bytes,
            error_message=error_msg,
        )
        db.add(record)
        db.commit()
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed to save OCR record")


def _load_index_html() -> str:
    """Load the single-page UI."""
    html_path = Path(__file__).with_suffix("").parent / "static" / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return _DEFAULT_HTML


_DEFAULT_HTML = """<!doctype html>
<html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FIT-OCR</title>
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
  select{background:#333;color:#fff;border:1px solid #555;padding:.3rem .6rem;border-radius:4px}
  @media(max-width:768px){.panes{grid-template-columns:1fr;grid-template-rows:1fr 1fr 1fr;height:auto}.pane{height:60vh}}
</style></head><body>
<header>
  <h1>📐 FIT-OCR</h1>
  <label class="btn">📷 拍照/选图<input type="file" id="file" accept="image/*" capture="environment"></label>
  <button id="go" disabled>识别</button>
  <select id="engine">
    <option value="fallback">🔄 自动 (本地→云端)</option>
    <option value="local">🏠 仅本地</option>
    <option value="cloud">☁️ 仅云端</option>
  </select>
  <span id="status">等待选图</span>
</header>
<div class="panes">
  <div class="pane"><h2>原图</h2><img id="img" class="preview"></div>
  <div class="pane"><h2>渲染</h2><div id="rendered">尚无结果</div></div>
  <div class="pane"><h2>LaTeX 源码</h2><textarea id="src" placeholder="识别结果将在这里显示，可编辑"></textarea></div>
</div>
<script>
const $file=document.getElementById('file'),$img=document.getElementById('img'),$go=document.getElementById('go'),$stat=document.getElementById('status'),$src=document.getElementById('src'),$ren=document.getElementById('rendered'),$eng=document.getElementById('engine');let currentFile=null;
$file.addEventListener('change',e=>{const f=e.target.files[0];if(!f)return;currentFile=f;$img.src=URL.createObjectURL(f);$stat.textContent=f.name+' ('+(f.size/1024).toFixed(0)+' KB)';$go.disabled=false;});
$go.addEventListener('click',async()=>{if(!currentFile)return;$go.disabled=true;$stat.textContent='识别中…';const fd=new FormData();fd.append('file',currentFile);fd.append('engine',$eng.value);const t0=performance.now();const r=await fetch('/recognize',{method:'POST',body:fd});const j=await r.json();const t=((performance.now()-t0)/1000).toFixed(1);if(!r.ok){$stat.textContent='错误: '+(j.detail||j.error);$go.disabled=false;return;}const label=j.engine==='pix2text-local'?'🏠本地':j.engine==='glm-4v-cloud'?'☁️云端':'🔄自动';$stat.textContent=`${label} · ${t}s · ${j.markdown.length} 字符`;$src.value=j.markdown;renderMarkdown(j.markdown);$go.disabled=false;});
$src.addEventListener('input',()=>renderMarkdown($src.value));
function renderMarkdown(md){let html=md.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n\n+/g,'</p><p>').replace(/\n/g,'<br>');$ren.innerHTML='<p>'+html+'</p>';if(window.renderMathInElement)renderMathInElement($ren,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false},{left:'\\(',right:'\\)',display:false},{left:'\\[',right:'\\]',display:true}],throwOnError:false});}
</script>
</body></html>"""
