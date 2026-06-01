# API Documentation

Base URL: `/api/v1`

## Auth
- `POST /auth/register` — create user and free subscription.
- `POST /auth/login` — exchange email/password for JWT.
- `POST /auth/google` — exchange a Google OAuth ID token for an application JWT.
- `GET /auth/me` — current user profile.

## Projects
- `GET /projects` — list authenticated user's projects.
- `POST /projects` — create project.
- `GET /projects/{project_id}` — fetch project.
- `POST /projects/{project_id}/generations` — run Gemini/LangGraph architecture workflow.
- `GET /projects/{project_id}/generations` — list history.

## Generations
- `GET /generations/{generation_id}` — fetch saved output including diagrams.
- `GET /generations/{generation_id}/export?format=markdown` — download Markdown.
- `GET /generations/{generation_id}/export?format=json` — download JSON.

## Billing
- `GET /billing/subscription` — plan and usage counters.
- `POST /billing/checkout` — create Stripe Checkout session when Stripe env vars are configured.

Interactive OpenAPI is available at `/docs`; raw schema is `/api/v1/openapi.json`.
