"""Test health endpoint."""
import urllib.request, json
try:
    with urllib.request.urlopen("http://localhost:8001/health", timeout=5) as r:
        print(json.loads(r.read().decode()))
except Exception as e:
    print("ERROR:", e)
