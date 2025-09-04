import json
import os
import sys

# Ensure we can import the FastAPI app from the monorepo path
# ../packages/pandas-ai/server
SERVER_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "packages",
    "pandas-ai",
    "server",
)
SERVER_DIR = os.path.abspath(SERVER_DIR)
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

try:
    from core.server import app  # type: ignore
except Exception as e:
    print(f"ERROR: Could not import FastAPI app: {e}")
    sys.exit(1)

routes = []
for r in app.routes:  # type: ignore[attr-defined]
    try:
        methods = sorted(list(getattr(r, "methods", []) or []))
    except Exception:
        methods = []
    routes.append(
        {
            "path": getattr(r, "path", str(r)),
            "methods": methods,
            "name": getattr(r, "name", None),
        }
    )

print(json.dumps(routes, indent=2))
