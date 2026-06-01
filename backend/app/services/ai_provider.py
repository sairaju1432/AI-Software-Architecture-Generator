import json
import re
from typing import Any

import httpx

from app.agents.prompts import AGENT_STEPS, SYSTEM_PROMPT
from app.core.config import get_settings

REQUIRED_OUTPUT_KEYS = [
    "functional_requirements",
    "non_functional_requirements",
    "recommended_architecture",
    "microservices",
    "database_schema",
    "rest_api_design",
    "folder_structure",
    "cicd_strategy",
    "docker_configuration",
    "kubernetes_plan",
    "aws_recommendation",
    "cost_estimation",
    "mermaid_diagrams",
]

LIST_KEYS = {"functional_requirements", "non_functional_requirements", "microservices"}


class GeminiArchitectureProvider:
    def __init__(self):
        self.settings = get_settings()

    async def generate(self, prompt: str) -> dict[str, Any]:
        if not self.settings.gemini_api_key:
            return self._deterministic_response(prompt)

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.gemini_model}:generateContent?key={self.settings.gemini_api_key}"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"{SYSTEM_PROMPT}\nAgents:\n"
                                + "\n".join(AGENT_STEPS)
                                + f"\nUser requirements:\n{prompt}"
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2,
            },
        }

        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return self._normalize(self._parse_json(text))

    def _parse_json(self, text: str) -> dict[str, Any]:
        cleaned = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            raise ValueError("Gemini returned a non-object JSON payload")
        return parsed

    def _normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(data)
        for key in REQUIRED_OUTPUT_KEYS:
            if key not in normalized:
                normalized[key] = [] if key in LIST_KEYS else {}
        diagrams = normalized.setdefault("mermaid_diagrams", {})
        diagrams.setdefault("system", "graph TD\nUser-->Web\nWeb-->API")
        diagrams.setdefault("erd", "erDiagram\nUSERS ||--o{ PROJECTS : owns")
        diagrams.setdefault("service_communication", "sequenceDiagram\nUser->>API: Generate")
        return normalized

    def _deterministic_response(self, prompt: str) -> dict[str, Any]:
        domain = prompt[:120]
        return self._normalize(
            {
                "functional_requirements": [
                    "User account management",
                    "Project workspaces",
                    "AI architecture generation",
                    "Export to Markdown/JSON",
                    "Generation history",
                ],
                "non_functional_requirements": [
                    "99.9% availability",
                    "Horizontal scalability",
                    "OWASP-aligned security",
                    "P95 API latency under 500ms except AI jobs",
                    "Auditable usage tracking",
                ],
                "recommended_architecture": {
                    "style": "modular monolith evolving to microservices",
                    "summary": f"Cloud-native SaaS for: {domain}",
                    "components": [
                        "Next.js web",
                        "FastAPI API",
                        "PostgreSQL",
                        "Redis",
                        "Gemini AI provider",
                        "Stripe billing",
                    ],
                },
                "microservices": [
                    {"name": "identity", "responsibility": "auth and profiles"},
                    {"name": "workspace", "responsibility": "projects and generations"},
                    {"name": "ai-orchestrator", "responsibility": "LangGraph-style agent pipeline"},
                    {"name": "billing", "responsibility": "subscriptions and metering"},
                ],
                "database_schema": {
                    "tables": {
                        "users": ["id", "email", "hashed_password", "google_sub"],
                        "projects": ["id", "user_id", "name", "description"],
                        "generations": ["id", "project_id", "prompt", "status"],
                        "architecture_outputs": ["id", "generation_id", "json sections"],
                        "subscriptions": ["id", "user_id", "plan", "monthly_generation_count"],
                    },
                    "indexes": ["users.email", "projects.user_id", "generations.project_id"],
                },
                "rest_api_design": {
                    "endpoints": [
                        "POST /auth/register",
                        "POST /auth/login",
                        "POST /auth/google",
                        "GET /projects",
                        "POST /projects",
                        "POST /projects/{id}/generations",
                        "GET /generations/{id}/export",
                    ]
                },
                "folder_structure": {
                    "frontend": ["app", "components", "lib"],
                    "backend": ["app/api", "app/models", "app/services", "alembic"],
                },
                "cicd_strategy": {"pipeline": ["lint", "test", "build images", "scan", "deploy"]},
                "docker_configuration": {"services": ["frontend", "backend", "postgres", "redis", "nginx"]},
                "kubernetes_plan": {"objects": ["Deployments", "Services", "Ingress", "Secrets", "HPA"]},
                "aws_recommendation": {
                    "compute": "EKS or ECS Fargate",
                    "database": "RDS PostgreSQL",
                    "cache": "ElastiCache Redis",
                    "secrets": "Secrets Manager",
                },
                "cost_estimation": {
                    "free_dev": "$0-25/mo",
                    "production_start": "$150-400/mo",
                    "scale": "optimize with autoscaling and committed usage",
                },
                "mermaid_diagrams": {
                    "system": "graph TD\nUser-->Web[Next.js]\nWeb-->API[FastAPI]\nAPI-->DB[(PostgreSQL)]\nAPI-->Redis[(Redis)]\nAPI-->Gemini[Gemini API]",
                    "erd": "erDiagram\nUSERS ||--o{ PROJECTS : owns\nPROJECTS ||--o{ GENERATIONS : has\nGENERATIONS ||--|| ARCHITECTURE_OUTPUTS : creates\nUSERS ||--|| SUBSCRIPTIONS : has",
                    "service_communication": "sequenceDiagram\nparticipant U as User\nparticipant W as Web\nparticipant A as API\nparticipant G as Gemini\nU->>W: submit requirements\nW->>A: create generation\nA->>G: run agents\nG-->>A: JSON architecture\nA-->>W: saved result",
                },
            }
        )
