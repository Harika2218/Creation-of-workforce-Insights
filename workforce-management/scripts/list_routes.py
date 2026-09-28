import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import app

print("=" * 60)
print("REGISTERED FASTAPI ROUTES")
print("=" * 60)
openapi = app.openapi()
paths = openapi.get("paths", {})

endpoints = []
for path, methods in paths.items():
    for method, details in methods.items():
        endpoints.append((method.upper(), path, details.get("summary", "")))

endpoints.sort(key=lambda x: (x[1], x[0]))
for method, path, summary in endpoints:
    print(f"{method:<8} {path:<45} : {summary}")

print("=" * 60)
print(f"Total Unique Endpoints: {len(endpoints)}")
