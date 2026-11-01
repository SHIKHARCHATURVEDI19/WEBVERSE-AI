# WebVerse AI — Codex Engineering Rules

## Product
WebVerse AI turns natural-language prompts into complete, responsive, multi-page websites with interactive 3D scenes. Users refine generated websites through conversational prompts. The initial supported categories are developer portfolios and restaurants.

## Engineering role
Act as a principal full-stack engineer and AI automation engineer. Make small, reviewable changes. Inspect the repository before editing. Do not rewrite working code unnecessarily. Explain architectural trade-offs briefly and test every change.

## Current milestone
This repository is a starter foundation, not a finished product. The current implementation includes:
- A Next.js Studio shell with a cream / burnt-orange visual identity.
- A FastAPI mock generation endpoint.
- A shared SiteSpec JSON Schema and example specification.
- A React Three Fiber procedural 3D hero scaffold.
- PostgreSQL and Redis development services in Docker Compose.

The first target is a working prompt → mock SiteSpec → preview flow without any paid API calls.

## Architecture rules
1. SiteSpec is the source of truth for generated websites.
2. The AI must produce validated structured data, not unrestricted HTML or JavaScript.
3. The renderer uses an allowlisted component registry and typed component props.
4. Prompt edits should create targeted, validated SiteSpec patches; do not regenerate the whole site for small changes.
5. Store project versions as immutable snapshots.
6. Keep the AI provider behind an interface. The default provider must be a deterministic mock and must not call an external model.
7. Agent nodes must have typed inputs, typed outputs, bounded retries and explicit tool permissions.
8. Run expensive or untrusted builds in isolated containers, never in the API process.

## Frontend rules
- Next.js App Router, TypeScript strict mode.
- Use server components by default; add `use client` only when browser interaction is needed.
- Keep components small and accessible.
- Use semantic HTML, keyboard focus states and responsive layouts.
- 3D scenes must have a loading/fallback strategy and respect reduced-motion preferences.
- Never let generated SiteSpec values become arbitrary executable code.

## Backend rules
- FastAPI with Pydantic validation and explicit response models.
- Validate incoming payloads and return useful HTTP errors.
- Read configuration from environment variables; never commit secrets.
- Add tests for schemas, generation endpoints and patch operations.
- Do not add LangGraph or a paid model client until the mock generation flow and schema are stable.

## Cost and model rules
- Codex is the development tool; it is not the runtime inference API for WebVerse users.
- Do not make paid API calls during development unless the user explicitly configures and approves a runtime provider.
- Track token usage and estimated cost for every real model call once providers are added.
- Add per-run budgets, rate limits, caching and bounded retries before enabling real generation.

## Security rules
- Never execute arbitrary model-generated code in the main application server.
- Use a strict component/prop allowlist and validate SiteSpec.
- Isolate previews from the Studio origin where practical.
- Restrict network access, CPU, memory, disk and execution time in build containers.
- Treat prompts, uploaded files, model output and imported assets as untrusted input.

## Definition of done
Before calling a task complete:
1. Run relevant linting, type checks and tests.
2. Check the production build when practical.
3. Report changed files and commands executed.
4. State any unverified behaviour or remaining limitation.
5. Do not claim tests passed unless they were actually run.

## Next implementation sequence
1. Verify and improve the Studio prompt-to-mock-generation flow.
2. Implement SiteSpec TypeScript types from the shared JSON Schema.
3. Build the component registry and renderer for portfolio and restaurant specs.
4. Add real preview routing and version snapshots.
5. Add prompt editing as validated JSON Patch operations.
6. Add LangGraph agents only after the deterministic pipeline is tested.

## Model selection and usage strategy

Use the following recommendations whenever selecting a model manually in Codex.

### Model selection strategy

1. GPT-6.1 Sol
   - System architecture
   - Complex multi-agent workflows
   - LangGraph orchestration
   - Difficult debugging
   - Security and architectural reviews
   - Complex refactoring

2. GPT-6.1 Terra
   - Next.js and React development
   - FastAPI implementation
   - Database development
   - Three.js and React Three Fiber
   - Regular feature implementation
   - Integration work

3. GPT-6 Luna
   - Documentation
   - Simple bug fixes
   - Small UI modifications
   - Formatting and straightforward code changes

### Credit optimization

- Prefer Terra for routine implementation.
- Reserve Sol for tasks requiring advanced reasoning.
- Use Luna for straightforward tasks.
- Never use a stronger model unnecessarily.
- Run automated tests, linting and type checking instead of using AI for repetitive verification.
- Avoid unnecessary full-project regeneration.
- Keep tasks focused and minimize repeated context.
- Do not make unnecessary API calls.

### Model selection limitation

These are recommendations, not automatic model-switching commands. Never claim to have switched models. The developer must select the model manually in the Codex interface.

If a recommended model is unavailable, use the closest available alternative.

### Reporting

At the end of each milestone, report:
- Work completed
- Tests passed and failed
- Remaining tasks
- Recommended model for the next milestone
- Whether a model change is recommended
