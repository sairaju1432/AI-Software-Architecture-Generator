# AI Software Architecture Generator SaaS

A production-ready full-stack SaaS starter that turns natural-language product ideas into complete software architecture plans, database designs, REST API specifications, DevOps plans, AWS deployment recommendations, cost estimates, and Mermaid diagrams.

## Stack

- **Frontend:** Next.js 15, TypeScript, Tailwind CSS, shadcn/ui-inspired components, dark/light mode, dashboard UI.
- **Backend:** FastAPI, PostgreSQL, SQLAlchemy 2, Alembic, JWT auth, Redis-ready caching, rate limiting, CORS, REST APIs.
- **AI layer:** Gemini API provider with a deterministic local fallback and a multi-agent workflow contract inspired by LangGraph/LangChain orchestration.
- **Infrastructure:** Docker Compose, Kubernetes manifests, Nginx reverse proxy, GitHub Actions CI.
- **Business:** Free/pro subscription model, usage tracking, Stripe environment contract.

## Quick start

```bash
cp .env.example .env
# Add GEMINI_API_KEY in .env for live Gemini generations; never commit real API keys.
docker compose up --build
```

Open:

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- Nginx gateway: http://localhost:8080

Seed a demo user after services start:

```bash
docker compose exec backend python scripts/seed.py
```

Demo credentials: `demo@example.com` / `ChangeMe123!`.

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
npm test
npm run build
```

## Environment variables

See `.env.example` for all configuration. Important production settings:

- `JWT_SECRET`: use a strong random secret.
- `DATABASE_URL`: PostgreSQL SQLAlchemy URL.
- `REDIS_URL`: Redis connection string.
- `GEMINI_API_KEY`: Google AI Studio/Gemini key for the free Gemini API tier.
- `CORS_ORIGINS`: allowed browser origins.
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID`: billing integration secrets and Pro price.
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: Google OAuth credentials. The backend verifies Google ID tokens at `/auth/google`.

## AI agent workflow

The backend sends one structured Gemini prompt representing six agents:

1. Requirements Analyst Agent
2. Tech Stack Recommendation Agent
3. Database Designer Agent
4. API Designer Agent
5. Architecture Generator Agent
6. DevOps Generator Agent

Gemini returns strict JSON sections that are normalized, cached in Redis by prompt, persisted in `architecture_outputs`, rendered by the dashboard, and exportable as Markdown or JSON.

## Security

- Password hashing with bcrypt/passlib.
- JWT bearer authentication.
- SQLAlchemy parameterized ORM access.
- Input validation with Pydantic.
- FastAPI CORS controls.
- SlowAPI rate-limit middleware.
- Secrets supplied by environment variables/Kubernetes Secrets.

## Deployment

### Docker Compose

`docker-compose.yml` runs PostgreSQL, Redis, FastAPI, Next.js and Nginx.

### Kubernetes

Apply manifests:

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/app.yaml
```

Recommended AWS production topology:

- EKS or ECS Fargate for containers.
- RDS PostgreSQL with automated backups.
- ElastiCache Redis.
- AWS Secrets Manager.
- ALB ingress with ACM TLS.
- CloudWatch logs/metrics and WAF.

## API documentation

See [`docs/API.md`](docs/API.md) or run the backend and open `/docs`.
