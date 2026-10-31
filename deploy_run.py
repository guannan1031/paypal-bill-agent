"""Public deployment entry point (reverse-proxy sandbox).

- Reads the injected $PORT environment variable (defaults to 8878 locally).
- Allows any Host header so the reverse-proxied public domain passes through.
"""
import os

import uvicorn
from starlette.middleware.trustedhost import TrustedHostMiddleware

from backend.app import create_app

app = create_app()

app.user_middleware = [
    m for m in app.user_middleware if m.cls is not TrustedHostMiddleware
]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8878")),
        workers=1,
        access_log=False,
    )
