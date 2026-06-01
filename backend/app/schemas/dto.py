from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.entities import GenerationStatus, Plan


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = ""


class UserRead(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(min_length=20)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    description: str = ""


class ProjectRead(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GenerationCreate(BaseModel):
    prompt: str = Field(min_length=20, max_length=12_000)


class ArchitectureOutputRead(BaseModel):
    functional_requirements: list
    non_functional_requirements: list
    recommended_architecture: dict
    microservices: list
    database_schema: dict
    rest_api_design: dict
    folder_structure: dict
    cicd_strategy: dict
    docker_configuration: dict
    kubernetes_plan: dict
    aws_recommendation: dict
    cost_estimation: dict
    mermaid_diagrams: dict
    raw: dict

    model_config = {"from_attributes": True}


class GenerationRead(BaseModel):
    id: str
    project_id: str
    prompt: str
    status: GenerationStatus
    error: str | None
    tokens_used: int
    created_at: datetime
    completed_at: datetime | None
    output: ArchitectureOutputRead | None = None

    model_config = {"from_attributes": True}


class SubscriptionRead(BaseModel):
    plan: Plan
    monthly_generation_count: int
    current_period_start: datetime

    model_config = {"from_attributes": True}


class CheckoutSessionRead(BaseModel):
    checkout_url: str
