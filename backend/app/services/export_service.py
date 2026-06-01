import json
from typing import Any

from app.models import Generation


class GenerationExportService:
    @staticmethod
    def to_json(generation: Generation) -> str:
        if not generation.output:
            return json.dumps({"error": "Generation has no output yet"}, indent=2)
        return json.dumps(generation.output.raw, indent=2)

    @staticmethod
    def to_markdown(generation: Generation) -> str:
        if not generation.output:
            return "# Architecture generation\n\nNo output is available yet."

        raw: dict[str, Any] = generation.output.raw
        sections = [
            f"# Architecture generation {generation.id}",
            "",
            "## Prompt",
            generation.prompt,
            "",
        ]
        labels = [
            ("Functional requirements", raw.get("functional_requirements", [])),
            ("Non-functional requirements", raw.get("non_functional_requirements", [])),
            ("Recommended architecture", raw.get("recommended_architecture", {})),
            ("Microservices", raw.get("microservices", [])),
            ("Database schema", raw.get("database_schema", {})),
            ("REST API design", raw.get("rest_api_design", {})),
            ("CI/CD strategy", raw.get("cicd_strategy", {})),
            ("Kubernetes plan", raw.get("kubernetes_plan", {})),
            ("AWS recommendation", raw.get("aws_recommendation", {})),
            ("Cost estimation", raw.get("cost_estimation", {})),
        ]
        for title, value in labels:
            sections.extend([f"## {title}", "", GenerationExportService._render(value), ""])

        diagrams = raw.get("mermaid_diagrams", {})
        for name, diagram in diagrams.items():
            sections.extend([f"## Mermaid: {name}", "", "```mermaid", str(diagram), "```", ""])
        return "\n".join(sections)

    @staticmethod
    def _render(value: Any) -> str:
        if isinstance(value, list):
            return "\n".join(f"- {item}" for item in value)
        return "```json\n" + json.dumps(value, indent=2) + "\n```"
