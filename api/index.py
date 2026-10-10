"""Vercel FastAPI entrypoint with diagnostic routing and path restoration."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

load_error = None
try:
    from backend.app import app as aroha_app
    base_app = aroha_app
except Exception as exc:
    load_error = f"{type(exc).__name__}: {str(exc)}"
    base_app = FastAPI()


class VercelPathMiddleware:
    """Restores the original request path from Vercel headers."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            raw_headers = dict(scope.get("headers", []))
            headers_decoded = {k.decode("latin1"): v.decode("latin1") for k, v in raw_headers.items()}
            
            # Diagnostic endpoint accessible at any path with ?diag=1
            query = scope.get("query_string", b"").decode("latin1")
            if "diag=1" in query or scope.get("path") in ["/api/diag", "/diag"]:
                response = JSONResponse({
                    "load_error": load_error,
                    "original_scope_path": scope.get("path"),
                    "headers": headers_decoded,
                    "root_contents": [p.name for p in PROJECT_ROOT.iterdir()] if PROJECT_ROOT.exists() else []
                })
                await response(scope, receive, send)
                return

            # Extract matched path
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
