import enum, uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Plan(str, enum.Enum):
    free = "free"
    pro = "pro"

class GenerationStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String(160), default="")
    google_sub: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    projects: Mapped[list["Project"]] = relationship(back_populates="owner", cascade="all,delete-orphan")
    subscription: Mapped["Subscription"] = relationship(back_populates="user", cascade="all,delete-orphan", uselist=False)

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner: Mapped[User] = relationship(back_populates="projects")
    generations: Mapped[list["Generation"]] = relationship(back_populates="project", cascade="all,delete-orphan")

class Generation(Base):
    __tablename__ = "generations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    status: Mapped[GenerationStatus] = mapped_column(Enum(GenerationStatus), default=GenerationStatus.queued)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    project: Mapped[Project] = relationship(back_populates="generations")
    output: Mapped["ArchitectureOutput"] = relationship(back_populates="generation", cascade="all,delete-orphan", uselist=False)

class ArchitectureOutput(Base):
    __tablename__ = "architecture_outputs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    generation_id: Mapped[str] = mapped_column(ForeignKey("generations.id", ondelete="CASCADE"), unique=True)
    functional_requirements: Mapped[list] = mapped_column(JSON, default=list)
    non_functional_requirements: Mapped[list] = mapped_column(JSON, default=list)
    recommended_architecture: Mapped[dict] = mapped_column(JSON, default=dict)
    microservices: Mapped[list] = mapped_column(JSON, default=list)
    database_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    rest_api_design: Mapped[dict] = mapped_column(JSON, default=dict)
    folder_structure: Mapped[dict] = mapped_column(JSON, default=dict)
    cicd_strategy: Mapped[dict] = mapped_column(JSON, default=dict)
    docker_configuration: Mapped[dict] = mapped_column(JSON, default=dict)
    kubernetes_plan: Mapped[dict] = mapped_column(JSON, default=dict)
    aws_recommendation: Mapped[dict] = mapped_column(JSON, default=dict)
    cost_estimation: Mapped[dict] = mapped_column(JSON, default=dict)
    mermaid_diagrams: Mapped[dict] = mapped_column(JSON, default=dict)
    raw: Mapped[dict] = mapped_column(JSON, default=dict)
    generation: Mapped[Generation] = relationship(back_populates="output")

class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("user_id"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan: Mapped[Plan] = mapped_column(Enum(Plan), default=Plan.free)
    stripe_customer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String, nullable=True)
    monthly_generation_count: Mapped[int] = mapped_column(Integer, default=0)
    current_period_start: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped[User] = relationship(back_populates="subscription")
