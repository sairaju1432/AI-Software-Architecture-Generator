SYSTEM_PROMPT = """You are a panel of senior SaaS architects. Return strict JSON only.
Generate a production architecture plan with these top-level keys: functional_requirements,
non_functional_requirements,recommended_architecture,microservices,database_schema,rest_api_design,
folder_structure,cicd_strategy,docker_configuration,kubernetes_plan,aws_recommendation,cost_estimation,
mermaid_diagrams. Include Mermaid strings for system, erd, and service_communication.
"""
AGENT_STEPS = [
    "Requirements Analyst Agent extracts product scope and acceptance criteria.",
    "Tech Stack Recommendation Agent selects cloud-native technologies.",
    "Database Designer Agent creates normalized schema and indexes.",
    "API Designer Agent creates REST resources, auth, errors, and examples.",
    "Architecture Generator Agent designs services, queues, events, and diagrams.",
    "DevOps Generator Agent creates Docker, Kubernetes, CI/CD, AWS, and cost plan.",
]
