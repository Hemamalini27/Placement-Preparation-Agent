import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.config import settings
from backend.database import db
from backend.routes.api import router as api_router
from backend.auth.routes import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect database (or fallback to in‑memory)
    await db.connect()
    yield
    # Any graceful shutdown logic would go here

app = FastAPI(
    title="Placement Preparation Agent API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS – keep it open for local testing / Vercel preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers – auth first so `/api/auth/*` works
app.include_router(auth_router)
app.include_router(api_router)

# ----------------------------------------------------------------------
# Static SPA handling (only used when running locally; Vercel serves via
# the `vercel.json` routes).  The logic stays harmless on Vercel.
# ----------------------------------------------------------------------
def _frontend_path() -> str:
    # Resolve the path relative to THIS file (works both locally and in Vercel)
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend")
    )

frontend_path = _frontend_path()
if os.path.isdir(frontend_path):
    # Serve `index.html` at the root when the folder exists
    @app.get("/", response_class=FileResponse)
    async def root() -> FileResponse:
        return FileResponse(os.path.join(frontend_path, "index.html"))

    # Mount the whole folder for CSS, JS, images, etc.
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    # Fail‑safe endpoint for CI / lint runs
    @app.get("/", response_class=FileResponse)
    async def dummy_root() -> FileResponse:
        return FileResponse("README.md")  # any static file – never used in production
