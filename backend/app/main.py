from **future** import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Root endpoint (Railway health check friendly)

@app.get("/")
def root():
return {
"service": "ABS Industrial Intelligence Platform",
"status": "running"
}

# Health check endpoint

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
return HealthResponse(
status="ok",
timestamp=datetime.now(timezone.utc)
)

# Include API routes

app.include_router(api_router, prefix=settings.api_prefix)
