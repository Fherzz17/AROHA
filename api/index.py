"""Vercel FastAPI entrypoint with deterministic path restoration."""

import os
import sys
import traceback
import urllib.parse
from pathlib import Path

# Ensure root paths are on sys.path
this_file = Path(__file__).resolve()
this_dir = this_file.parent
parent_dir = this_dir.parent
cwd = Path.cwd().resolve()

for p in [str(cwd), str(parent_dir), str(this_dir), "/var/task"]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI
from starlette.types import ASGIApp, Receive, Scope, Send

try:
    from backend.app import app as aroha_app
    base_app = aroha_app
except Exception as exc:
    err_trace = traceback.format_exc()
    base_app = FastAPI()

    @base_app.get("/api/health")
    def health_fallback():
        return {"error": err_trace}


class VercelPathMiddleware:
    """Restores the original request path from the captured __path query param."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            query_str = scope.get("query_string", b"").decode("latin1")
            if "__path=" in query_str:
                params = urllib.parse.parse_qs(query_str)
                real_path = params.get("__path", ["/"])[0]
                if not real_path.startswith("/"):
                    real_path = "/" + real_path
                scope["path"] = real_path

                # Remove internal __path from query string
                clean_params = {k: v for k, v in params.items() if k != "__path"}
                scope["query_string"] = urllib.parse.urlencode(clean_params, doseq=True).encode("latin1")
            elif scope.get("path") == "/api/index.py":
                scope["path"] = "/"

        await self.app(scope, receive, send)


app = VercelPathMiddleware(base_app)

__all__ = ["app"]
