"""Vercel FastAPI entrypoint."""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI


app = FastAPI()

try:
    from backend.app import app as aroha_app

    app = aroha_app
except ModuleNotFoundError:
    @app.get("/api/health")
    def bundle_diagnostic():
        return {
            "function_root": str(PROJECT_ROOT),
            "root_entries": sorted(path.name for path in PROJECT_ROOT.iterdir()),
            "vendor_entries": sorted(
                path.name for path in (PROJECT_ROOT / "_vendor").iterdir()
            ) if (PROJECT_ROOT / "_vendor").exists() else [],
        }

__all__ = ["app"]
