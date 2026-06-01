import hashlib
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.workflow import build_architecture_workflow
from app.core.config import get_settings
from app.models import ArchitectureOutput, Generation, GenerationStatus, Plan, Project, Subscription
from app.services.ai_provider import REQUIRED_OUTPUT_KEYS
from app.services.cache import Cache


class GenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.cache = Cache()
        self.workflow = build_architecture_workflow()

    def _ensure_quota(self, subscription: Subscription) -> None:
        if subscription.plan == Plan.free and subscription.monthly_generation_count >= get_settings().free_monthly_generations:
            raise HTTPException(status_code=402, detail="Free tier generation limit reached. Upgrade to Pro.")

    async def create_generation(self, project: Project, prompt: str) -> Generation:
        subscription = project.owner.subscription
        self._ensure_quota(subscription)

        generation = Generation(project_id=project.id, prompt=prompt, status=GenerationStatus.running)
        self.db.add(generation)
        self.db.commit()
        self.db.refresh(generation)

        try:
            result = await self._generate_or_load_cached(project.id, prompt)
            output_payload = {key: result.get(key, [] if key in {"functional_requirements", "non_functional_requirements", "microservices"} else {}) for key in REQUIRED_OUTPUT_KEYS}
            output = ArchitectureOutput(generation_id=generation.id, raw=result, **output_payload)
            generation.status = GenerationStatus.completed
            generation.completed_at = datetime.utcnow()
            generation.tokens_used = max(1, len(prompt.split()) * 2)
            subscription.monthly_generation_count += 1
            self.db.add(output)
        except Exception as exc:
            generation.status = GenerationStatus.failed
            generation.error = str(exc)

        self.db.commit()
        self.db.refresh(generation)
        return generation

    async def _generate_or_load_cached(self, project_id: str, prompt: str) -> dict:
        cache_key = "generation:" + hashlib.sha256(f"{project_id}:{prompt}".encode()).hexdigest()
        cached = self.cache.get_json(cache_key)
        if cached:
            return cached
        workflow_state = await self.workflow.ainvoke({"prompt": prompt, "notes": []})
        result = workflow_state["output"]
        self.cache.set_json(cache_key, result)
        return result
