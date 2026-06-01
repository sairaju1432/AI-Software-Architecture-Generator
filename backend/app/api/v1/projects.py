from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Generation, Project, User
from app.schemas.dto import GenerationCreate, GenerationRead, ProjectCreate, ProjectRead
from app.services.generation_service import GenerationService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.query(Project).filter(Project.user_id == user.id).order_by(Project.updated_at.desc()).all()


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    project = Project(user_id=user.id, name=payload.name, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/generations", response_model=GenerationRead, status_code=201)
async def generate(project_id: str, payload: GenerationCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    project = (
        db.query(Project)
        .options(selectinload(Project.owner).selectinload(User.subscription))
        .filter(Project.id == project_id, Project.user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await GenerationService(db).create_generation(project, payload.prompt)


@router.get("/{project_id}/generations", response_model=list[GenerationRead])
def generations(project_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return (
        db.query(Generation)
        .options(selectinload(Generation.output))
        .filter(Generation.project_id == project_id)
        .order_by(Generation.created_at.desc())
        .all()
    )
