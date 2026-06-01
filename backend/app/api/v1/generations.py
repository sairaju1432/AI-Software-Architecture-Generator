from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session, selectinload

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Generation, User
from app.schemas.dto import GenerationRead
from app.services.export_service import GenerationExportService

router = APIRouter(prefix="/generations", tags=["generations"])


@router.get("/{generation_id}", response_model=GenerationRead)
def get_generation(generation_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    generation = (
        db.query(Generation)
        .options(selectinload(Generation.output), selectinload(Generation.project))
        .filter(Generation.id == generation_id)
        .first()
    )
    if not generation or generation.project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Generation not found")
    return generation


@router.get("/{generation_id}/export")
def export_generation(
    generation_id: str,
    format: str = "markdown",
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    generation = (
        db.query(Generation)
        .options(selectinload(Generation.output), selectinload(Generation.project))
        .filter(Generation.id == generation_id)
        .first()
    )
    if not generation or generation.project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Generation not found")

    if format == "json":
        return Response(
            GenerationExportService.to_json(generation),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="generation-{generation.id}.json"'},
        )
    if format != "markdown":
        raise HTTPException(status_code=400, detail="format must be 'markdown' or 'json'")
    return Response(
        GenerationExportService.to_markdown(generation),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="generation-{generation.id}.md"'},
    )
