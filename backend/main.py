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
    # Connect database
    await db.connect()
    yield
    # Close resources if any

app = FastAPI(
    title="Placement Preparation Agent API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local cross-origin testing/debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints
app.include_router(auth_router)
app.include_router(api_router)

# Serve SPA Frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_path):
    # Serve index.html as homepage
    @app.get("/")
    async def get_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    # Mount the rest of the folder for CSS, JS, etc.
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    # Fail-safe endpoint if frontend files are missing locally during compile checks
    @app.get("/")
    async def root():
        return {"status": "success", "message": "Placement Preparation Agent API is running. Frontend folder not found."}
