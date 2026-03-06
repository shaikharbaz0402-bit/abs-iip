from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.db.init_db import init_db
from app.schemas.common import HealthResponse

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Multi-tenant industrial bolt integrity monitoring and analytics SaaS platform.",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event (initialize database)
@app.on_event("startup")
def startup_event() -> None:
    init_db()


# Root landing page
@app.get("/", response_class=HTMLResponse)
def landing_page() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset='utf-8'/>
    <meta name='viewport' content='width=device-width, initial-scale=1'/>
    <title>ABS Industrial Intelligence Platform</title>
    <style>
      body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin:0; background:#f4f7fb; color:#0f172a; }
      .hero { min-height:100vh; display:flex; align-items:center; justify-content:center; }
      .card { width:min(760px,92vw); background:white; border-radius:16px; padding:40px; box-shadow:0 20px 40px rgba(0,0,0,.08); }
      h1 { margin:0 0 12px; font-size:34px; }
      p { color:#334155; }
      .actions { margin-top:24px; display:flex; gap:14px; flex-wrap:wrap; }
      a.btn { text-decoration:none; padding:12px 18px; border-radius:10px; font-weight:600; }
      .abs { background:#0f4c81; color:white; }
      .client { background:#1f2937; color:white; }
    </style>
  </head>
  <body>
    <div class='hero'>
      <div class='card'>
        <h1>ABS Industrial Intelligence Platform</h1>
        <p>Enterprise multi-tenant SaaS for digital joint integrity, engineering analytics, and quality certification.</p>
        <div class='actions'>
          <a class='btn abs' href='/docs'>Login as ABS Engineer</a>
          <a class='btn client' href='/docs'>Login as Client</a>
        </div>
      </div>
    </div>
  </body>
</html>
    """


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc)
    )


# Include API routes
app.include_router(api_router, prefix=settings.api_prefix)