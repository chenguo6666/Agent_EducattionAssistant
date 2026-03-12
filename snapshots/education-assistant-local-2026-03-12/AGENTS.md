# Project Agent Notes

## Project Summary

- Project: Education Assistant AI Agent
- Goal: Build a course project MVP with a Vue frontend and FastAPI backend.
- Process: Scrum with 3 sprints. Treat Sprint 1 as the active delivery target until the user changes scope.

## Active Technical Decisions

- Frontend: Vue 3 + Vite + TypeScript + Vue Router + Pinia
- Backend: FastAPI + SQLAlchemy + SQLite
- Agent layer: LangChain-ready structure, but keep Sprint 1 logic simple and controllable.
- Output rendering: Markdown on the frontend
- Task statuses: `submitted`, `analyzing`, `executing`, `completed`, `failed`

## Delivery Rules

- Do not pull Sprint 2 or Sprint 3 features into Sprint 1 unless the user explicitly asks.
- Prefer small, testable increments over broad scaffolding with no runtime value.
- Keep backend interfaces stable once `docs/project-preparation.md` is updated.
- Do not expose real chain-of-thought. Show step/status summaries instead.

## Collaboration Context

- The user works in the Codex Windows app and also opens the repo in Cursor.
- The user uses GPT-5.4 for discussion and decision-making.
- The user switches to GPT-5.3-codex when they want direct code implementation work.
- Keep project docs in sync when architecture or interface decisions change.

## Current Folder Intent

- `frontend/`: Vue application
- `backend/`: FastAPI application
- `docs/`: planning and architecture documents

## Initialization Goal

During project initialization, ensure the repo contains:

- a runnable frontend skeleton
- a runnable backend skeleton
- environment example files
- stable folders for auth, chat, agent, tools, models, and services
