"""Light import verification — no model loading."""
import sys

print("Python:", sys.version.split()[0])
print()

checks = [
    ("server", "server"),
    ("server.core.models", "server.core.models"),
    ("server.core.interfaces", "server.core.interfaces"),
    ("server.core.exceptions", "server.core.exceptions"),
    ("server.engines.local", "server.engines.local"),
    ("server.engines.cloud", "server.engines.cloud"),
    ("server.engines.fallback", "server.engines.fallback"),
    ("server.infrastructure.config", "server.infrastructure.config"),
    ("server.api.app", "server.api.app"),
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
