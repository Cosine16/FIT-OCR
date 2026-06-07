"""Test the FIT-OCR API with a local image."""
import json
import sys
from pathlib import Path
import urllib.request

img = Path(__file__).parent.parent / "samples" / "synthetic_math.png"
url = "http://localhost:8001/recognize"

boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="{img.name}"\r\n'
    f"Content-Type: image/png\r\n\r\n"
).encode() + img.read_bytes() + f"\r\n--{boundary}--\r\n".encode()

req = urllib.request.Request(
    url,
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
        print("status:", resp.status)
        print("elapsed_s:", data.get("elapsed_s"))
        print("markdown:")
        print(data.get("markdown", "N/A"))
except Exception as e:
    print("ERROR:", e)
    sys.exit(1)
