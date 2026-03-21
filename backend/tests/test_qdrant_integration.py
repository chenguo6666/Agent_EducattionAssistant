import asyncio
import io
import json
import math
import threading
import unittest
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from unittest.mock import patch

from fastapi import UploadFile

from app.core.config import settings
from app.core.database import SessionLocal
from app.main import app  # noqa: F401
from app.models.chat_session import ChatSession
from app.models.document_chunk import DocumentChunk
from app.models.uploaded_document import UploadedDocument
from app.models.user import User
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from migrate_qdrant import migrate


def _vector_for_text(text: str) -> list[float]:
    normalized = text.lower()
    if any(token in normalized for token in ["工业", "社会问题", "贫富", "城市化"]):
        return [1.0, 0.0]
    return [0.0, 1.0]


class _FakeQdrantHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A003
        return

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        return json.loads(raw.decode("utf-8")) if raw else {}

    def _write_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        parts = [part for part in parsed.path.split("/") if part]
        state = self.server.state

        if parts == ["collections"]:
            self._write_json({"result": [{"name": name} for name in state["collections"].keys()], "status": "ok"})
            return

        if len(parts) == 2 and parts[0] == "collections":
            collection = parts[1]
            if collection not in state["collections"]:
                self._write_json({"status": "error"}, status=404)
                return
            self._write_json({"result": {"config": state["collections"][collection]}, "status": "ok"})
            return

        self._write_json({"status": "error"}, status=404)

    def do_PUT(self):  # noqa: N802
        parsed = urlparse(self.path)
        parts = [part for part in parsed.path.split("/") if part]
        state = self.server.state
        payload = self._read_json()

        if len(parts) == 2 and parts[0] == "collections":
            state["collections"][parts[1]] = payload.get("vectors", {})
            self._write_json({"result": True, "status": "ok"})
            return

        if len(parts) == 3 and parts[0] == "collections" and parts[2] == "points":
            collection = parts[1]
            state["points"].setdefault(collection, {})
            for point in payload.get("points", []):
                state["points"][collection][int(point["id"])] = point
            self._write_json({"result": {"status": "acknowledged"}, "status": "ok"})
            return

        self._write_json({"status": "error"}, status=404)

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        parts = [part for part in parsed.path.split("/") if part]
        state = self.server.state
        payload = self._read_json()

        if len(parts) == 4 and parts[0] == "collections" and parts[2] == "points" and parts[3] == "search":
            collection = parts[1]
            query_vector = payload.get("vector", [])
            limit = int(payload.get("limit", 5))
            must_filters = payload.get("filter", {}).get("must", [])
            points = list(state["points"].get(collection, {}).values())
            filtered = []
            for point in points:
                point_payload = point.get("payload", {})
                if all(point_payload.get(item.get("key")) == item.get("match", {}).get("value") for item in must_filters):
                    filtered.append(point)

            ranked = []
            for point in filtered:
                vector = point.get("vector", [])
                score = _cosine(query_vector, vector)
                ranked.append({"id": point["id"], "score": score, "payload": point.get("payload", {})})
            ranked.sort(key=lambda item: item["score"], reverse=True)
            self._write_json({"result": ranked[:limit], "status": "ok"})
            return

        if len(parts) == 4 and parts[0] == "collections" and parts[2] == "points" and parts[3] == "delete":
            collection = parts[1]
            must_filters = payload.get("filter", {}).get("must", [])
            kept = {}
            for point_id, point in state["points"].get(collection, {}).items():
                point_payload = point.get("payload", {})
                matched = all(point_payload.get(item.get("key")) == item.get("match", {}).get("value") for item in must_filters)
                if not matched:
                    kept[point_id] = point
            state["points"][collection] = kept
            self._write_json({"result": {"status": "acknowledged"}, "status": "ok"})
            return

        self._write_json({"status": "error"}, status=404)


def _cosine(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(x * y for x, y in zip(left, right))
    left_norm = math.sqrt(sum(x * x for x in left))
    right_norm = math.sqrt(sum(y * y for y in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


class QdrantIntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _FakeQdrantHandler)
        cls.server.state = {"collections": {}, "points": {}}
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        self.original_provider = settings.vector_store_provider
        self.original_url = settings.vector_store_url
        self.original_collection = settings.vector_store_collection
        settings.vector_store_provider = "qdrant"
        settings.vector_store_url = self.base_url
        settings.vector_store_collection = f"test_{uuid.uuid4().hex[:8]}"

        self.db = SessionLocal()
        self.user = User(
            username=f"qdrant_{uuid.uuid4().hex[:6]}",
            phone=f"1{uuid.uuid4().int % 10**10:010d}",
            password_hash="test",
        )
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        self.db.close()
        settings.vector_store_provider = self.original_provider
        settings.vector_store_url = self.original_url
        settings.vector_store_collection = self.original_collection

    def test_qdrant_upload_and_retrieve_flow(self):
        document_service = DocumentService()
        retrieval_service = RetrievalService()
        upload_file = UploadFile(filename="lesson.txt", file=io.BytesIO("工业革命推动了城市化，也带来了贫富分化等社会问题。".encode("utf-8")))

        with patch.object(EmbeddingService, "embed_documents", autospec=True, side_effect=lambda _self, texts: [_vector_for_text(text) for text in texts]), patch.object(
            EmbeddingService,
            "embed_query",
            autospec=True,
            side_effect=lambda _self, text: _vector_for_text(text),
        ):
            uploaded = asyncio.run(document_service.upload(db=self.db, user_id=self.user.id, file=upload_file))
            hits = retrieval_service.retrieve(
                db=self.db,
                user_id=self.user.id,
                session_id=uploaded.sessionId,
                query="工业革命带来了哪些社会问题",
                top_k=2,
            )

        self.assertGreaterEqual(len(hits), 1)
        self.assertIn("社会问题", hits[0].content)
        stored_points = self.server.state["points"][settings.vector_store_collection]
        self.assertGreaterEqual(len(stored_points), 1)

    def test_migrate_qdrant_indexes_existing_chunks(self):
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=self.user.id,
            title="migration",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(session)
        self.db.flush()

        document = UploadedDocument(
            id=str(uuid.uuid4()),
            user_id=self.user.id,
            session_id=session.id,
            file_name="history.txt",
            file_type="txt",
            content_type="text/plain",
            file_size=10,
            file_path="history.txt",
            extracted_text="工业革命带来了城市化。",
            extraction_status="completed",
        )
        self.db.add(document)
        self.db.flush()

        chunk = DocumentChunk(
            document_id=document.id,
            session_id=session.id,
            user_id=self.user.id,
            chunk_index=0,
            content="工业革命带来了城市化。",
            keywords_json=["工业革命", "城市化"],
            embedding_json=[1.0, 0.0],
        )
        self.db.add(chunk)
        self.db.commit()

        migrated = migrate(batch_size=8)
        self.assertGreaterEqual(migrated, 1)
        stored_points = self.server.state["points"][settings.vector_store_collection]
        self.assertIn(chunk.id, stored_points)


if __name__ == "__main__":
    unittest.main()
