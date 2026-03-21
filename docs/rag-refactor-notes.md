# RAG Refactor Notes

## Goal

Refactor the project from a lightweight in-process retrieval flow into a layered RAG architecture that is closer to a production system.

## New Layers

1. `DocumentService`
   - Owns file upload and text extraction.
   - Persists document metadata and chunk metadata.
2. `RagIngestionService`
   - Owns chunk embedding and vector index synchronization.
3. `Vector Store`
   - Abstract retrieval index layer.
   - `sqlite` backend keeps the project runnable by default.
   - `qdrant` backend is the formal external vector database option.
4. `RetrievalService`
   - Owns candidate loading, vector recall, keyword scoring, hybrid ranking, and context assembly.
5. `Agent Toolbox`
   - Calls retrieval as a tool and passes retrieved context into downstream answer generation.

## Runtime Strategy

- Default fallback: `VECTOR_STORE_PROVIDER=sqlite`
  - No extra infrastructure required.
  - Still uses the new layered design.
- Practical mode: `VECTOR_STORE_PROVIDER=qdrant`
  - Configure `VECTOR_STORE_URL` and optional `VECTOR_STORE_API_KEY`.
  - Chunk vectors are indexed into Qdrant.
  - SQLite continues to store business metadata.
  - The local scripts start backend in Qdrant mode automatically.

## Local Scripts

- `.\scripts\start-qdrant.ps1`
  - Starts a local Qdrant container with Docker.
- `.\scripts\dev-up.ps1`
  - Starts Qdrant, backend, and frontend together.
- `.\scripts\dev-check.ps1`
  - Verifies Qdrant, backend, and frontend are all reachable.
- `.\scripts\migrate-qdrant.ps1`
  - Re-indexes existing chunks from SQLite metadata into the configured vector store.

## Why This Is Better

- Business data and vector retrieval responsibilities are separated.
- Retrieval can evolve independently from upload logic.
- External vector databases can be introduced without rewriting the Agent layer.
- Hybrid ranking remains under backend control instead of being hidden inside a vendor SDK.
