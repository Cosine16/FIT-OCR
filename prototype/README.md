# FIT-OCR Prototype — THROWAWAY

> ⚠️ This is a **throwaway prototype** per `mattpocock-skills:prototype`.
> It exists to answer ONE question:
>
> **Can Pix2Text + UniMERNet actually run on a GTX 1650 4GB in WSL2, and
> does the result look good enough on real handwritten math notes?**
>
> If yes → fold validated decisions into real code in `OCR_server/`.
> If no → back to grill-me to pick a different model.
>
> **Do NOT build on top of this directly.** It has no tests, no error
> handling beyond runnability, and persistence is local-files-only.

## How to run

```bash
# from FIT-OCR/prototype/
source .venv/bin/activate
python smoke_test.py path/to/a_note_photo.jpg   # logic-branch smoke test
python app.py                                    # FastAPI Web UI on :8000
```

## Files

| File | Purpose |
|---|---|
| `smoke_test.py` | LOGIC branch — load models, run on 1 image, dump results. Pure verification. |
| `app.py` | UI branch — FastAPI single-file Web UI (3-pane: image / KaTeX render / source) |
| `samples/` | Drop test images here (handwritten math notes ideally) |
| `output/` | Generated .md / .json / png copies |

## What it tests
1. Models load on GPU (or fall back to CPU)
2. Pix2Text recognizes a mixed page → Markdown+LaTeX
3. UniMERNet recognizes a cropped formula → LaTeX
4. Web UI renders LaTeX via KaTeX without crashing
5. "Re-run with UniMERNet on selection" round-trip works
