from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.core.config import settings
from app.db.session import engine
from app.db.models import Base
from app.db.seed import seed
from app.api import auth, goals, agent, admin

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Seed demo data if empty
try:
    seed()
except Exception:
    pass

app = FastAPI(
    title="NextStep API",
    version="2.0.0",
    description="Agentic AI assistant for students — one step at a time.",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth.router)
app.include_router(goals.router)
app.include_router(agent.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "NextStep API v2", "mode": settings.LLM_PROVIDER}


# Serve React SPA from ../client/dist if it exists
client_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client", "dist"))
if os.path.isdir(client_dist):
    assets_dir = os.path.join(client_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        index = os.path.join(client_dist, "index.html")
        return FileResponse(index)
