from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from app.api.repositories import router
from app.api.mcp_router import router as mcp_router

from app.core.database import Base
from app.core.database import engine
from app.models.memory import FixPatternMemory


from app.api.scans import (
    router as scan_router
)
from app.api.dashboard import DASHBOARD_HTML

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BugBountyHunter"
)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(
    router,
    prefix="/api"
)

app.include_router(
    mcp_router,
    prefix="/api"
)


@app.get("/")
def health():
    return {
        "status": "ok"
    }


@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    return DASHBOARD_HTML


app.include_router(
    scan_router,
    prefix="/api"
)
