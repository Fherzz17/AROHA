"""Vercel FastAPI entrypoint with ASGI path restoration."""

import os
import sys
import traceback
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
    """Restores the original request path from Vercel headers."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            raw_headers = dict(scope.get("headers", []))
            headers_decoded = {k.decode("latin1"): v.decode("latin1") for k, v in raw_headers.items()}

            # Extract matched path from headers
            matched = (
                headers_decoded.get("x-matched-path")
                or headers_decoded.get("x-forwarded-uri")
                or headers_decoded.get("x-invoke-path")
                or headers_decoded.get("x-original-url")
            )
            if matched:
                path_only = matched.split("?")[0]
                if path_only and not path_only.startswith("/api/index.py"):
                    scope["path"] = path_only
                elif path_only == "/api/index.py":
                    scope["path"] = "/"
            elif scope.get("path") == "/api/index.py":
                scope["path"] = "/"

        await self.app(scope, receive, send)


app = VercelPathMiddleware(base_app)

__all__ = ["app"]
