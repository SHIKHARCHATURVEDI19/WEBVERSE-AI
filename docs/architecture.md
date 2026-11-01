# WebVerse AI — Initial Architecture

## First vertical slice

`Prompt UI → FastAPI → Mock Provider → validated SiteSpec → PostgreSQL version → version-bound preview`

The flow is intentionally deterministic and costs no inference credits. Each valid generation is committed as an immutable SiteSpec snapshot, and previews remain bound to the requested version even after later versions are created.

## Target architecture

- **Studio:** Next.js application for workspaces, prompts, previews and project history.
- **API:** FastAPI for authentication, project operations, generation requests and event streaming.
- **Worker:** LangGraph workflows for planner, design, content, 3D scene, frontend and QA tasks.
- **SiteSpec:** Validated JSON document describing pages, sections, design tokens, interactions and 3D scenes.
- **Renderer:** Allowlisted React components and React Three Fiber scene presets.
- **Persistence:** PostgreSQL for users/projects/versions/runs; object storage for images and 3D assets; Redis for queues and short-lived state.
- **Preview/build:** Isolated build and preview environment. Never execute arbitrary generated code in the API process.

## Key decision

The model produces structured data, not a free-form application. A deterministic renderer owns the code that is executed. Prompt editing will create validated patches against a specific section or page and save a new immutable version.

## Current limitations

- No authentication or user persistence yet; workspace isolation currently uses an explicit workspace header.
- No LangGraph or external model client yet.
- No persistent job queue or SSE events yet.
- No complete SiteSpec-to-site renderer yet.
- No deployment/export pipeline yet.
