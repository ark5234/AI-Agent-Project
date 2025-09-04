# Architecture Overview

This repository is organized as a small mono-repo with apps and packages.

- apps/
  - streamlit-app/: Streamlit data app for CSV/Google Sheets + CSE + Gemini
- packages/
  - pandas-ai/: Backend service (FastAPI server, NextJS client, Docker infra)
- infra/
  - docker-compose.yml (if used in root previously)
- docs/: Generated or static documentation
- scripts/: Utility scripts (e.g., route listers)

## Components

- Streamlit App (Python 3.11)
  - Data ingestion from CSV/Google Sheets
  - Google CSE search + Gemini fallback
  - Export/download

- Backend (FastAPI Python 3.11)
  - Users, Chat, Datasets, Conversations, Workspace, Monitoring
  - Async SQLAlchemy + Postgres
  - Auth via JWT (python-jose), password hashing (passlib/bcrypt)

- Frontend (Next.js 14)
  - Admin UI (workspaces, datasets, logs)

## Development

- Prefer separate virtualenvs per app.
- Use Docker Compose under `packages/pandas-ai` or `infra` for Postgres + server.
- Keep secrets out of Git; use .env and local secrets.
