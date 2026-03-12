from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import register_exception_handlers
from app.models import chat_session, document_chunk, mistake_record, task_record, uploaded_document, user


def upgrade_sqlite_schema() -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    if "task_records" in table_names:
        existing_columns = {column["name"] for column in inspector.get_columns("task_records")}
        required_columns = {
            "session_id": "ALTER TABLE task_records ADD COLUMN session_id VARCHAR(36)",
            "steps_json": "ALTER TABLE task_records ADD COLUMN steps_json JSON DEFAULT '[]' NOT NULL",
            "timeline_json": "ALTER TABLE task_records ADD COLUMN timeline_json JSON DEFAULT '[]' NOT NULL",
            "retrieved_chunks_json": "ALTER TABLE task_records ADD COLUMN retrieved_chunks_json JSON DEFAULT '[]' NOT NULL",
            "error_message": "ALTER TABLE task_records ADD COLUMN error_message TEXT",
        }

        with engine.begin() as connection:
            for column_name, statement in required_columns.items():
                if column_name not in existing_columns:
                    connection.execute(text(statement))

    if "document_chunks" in table_names:
        existing_columns = {column["name"] for column in inspector.get_columns("document_chunks")}
        if "embedding_json" not in existing_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE document_chunks ADD COLUMN embedding_json JSON"))


existing_tables = set(inspect(engine).get_table_names())
for table in (
    user.User.__table__,
    chat_session.ChatSession.__table__,
    task_record.TaskRecord.__table__,
    uploaded_document.UploadedDocument.__table__,
    document_chunk.DocumentChunk.__table__,
    mistake_record.MistakeRecord.__table__,
):
    if table.name not in existing_tables:
        table.create(bind=engine)

upgrade_sqlite_schema()
Path(settings.uploads_dir).resolve().mkdir(parents=True, exist_ok=True)

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
app.include_router(documents_router)

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
