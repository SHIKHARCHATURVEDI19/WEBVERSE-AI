# WebVerse AI

An AI website-generation studio for complete, responsive websites with interactive 3D scenes. This starter is intentionally **mock-first**: it does not require an OpenAI API key and does not make paid inference calls.

## Current starter capabilities

- Cream / burnt-orange Next.js Studio interface.
- Prompt form with Portfolio and Restaurant categories.
- FastAPI mock generation with persistent projects and immutable SiteSpec versions.
- PostgreSQL-backed project workspaces, version history, restoration and exact-version previews.
- Shared JSON Schema for website specifications.
- React Three Fiber procedural 3D scene scaffold.
- PostgreSQL and Redis services for local development.

> This is a foundation. It does not yet implement six autonomous agents, authentication, prompt patching, export or deployment.

## Requirements

- Node.js 22 or newer
- pnpm 10 or newer
- Python 3.11 or newer
- Docker Desktop (optional for PostgreSQL / Redis)

## Quick start

### 1. Install frontend dependencies

```bash
corepack enable
pnpm install
```

### 2. Start the Studio

```bash
pnpm dev:studio
```

Open http://localhost:3000.

### 3. Start the mock API

In a second terminal:

```bash
cd apps/api
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

For backend tests, install `requirements-dev.txt` and run `pytest -q` from `apps/api`.

The Studio calls `http://localhost:8000` by default. Override it with `NEXT_PUBLIC_API_URL` if needed.

### 4. Start infrastructure

```bash
docker compose -f infrastructure/compose.yaml up -d
```

PostgreSQL is exposed on `localhost:5432`; Redis is exposed on `localhost:6379`.

The Studio uses the `default` workspace until authentication is introduced. API clients may set `X-Workspace-ID` to enforce a separate workspace boundary.

## Model and credit policy

Codex is used to write the application. The mock API provider is used for runtime website-generation development. Do not add a paid inference call unless a runtime API provider is explicitly configured and approved. ChatGPT / Codex subscription usage is separate from application API billing.

## Repository layout

```text
apps/
  studio/       Next.js product UI
  api/          FastAPI backend (mock generation)
packages/
  site-schema/  Shared SiteSpec JSON Schema and example
infrastructure/ Docker Compose services
docs/           Architecture notes
AGENTS.md       Instructions for Codex
```

## Next milestones

1. Finish the prompt → mock generation → preview vertical slice.
2. Implement the SiteSpec type system and component registry.
3. Add restaurant and portfolio renderers.
4. Add project persistence and immutable versions.
5. Add safe prompt-based editing via validated patches.
6. Add LangGraph orchestration and specialist agents.
7. Add QA automation, isolated export builds and deployment.
