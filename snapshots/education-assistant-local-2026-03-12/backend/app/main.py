from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import register_exception_handlers
from app.models import task_record, user

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)

frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"

if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    def frontend_root():
        return FileResponse(frontend_dist / "index.html")

    @app.get("/favicon.svg", include_in_schema=False)
    def frontend_favicon():
        favicon_path = frontend_dist / "favicon.svg"
        return FileResponse(favicon_path) if favicon_path.exists() else JSONResponse({"detail": "Not Found"}, status_code=404)

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend_app(full_path: str):
        if full_path.startswith("api"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        return FileResponse(frontend_dist / "index.html")
