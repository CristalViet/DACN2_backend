from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app import models
from app.schemas import summary as schema
from app.core.deps import get_current_user

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.post("/", response_model=schema.SummaryResponse)
def create_summary(
    payload: schema.SummaryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # Only writers can create summaries; writer_id is derived from token
    role = db.get(models.user_role.UserRole, current_user.role_id) if current_user.role_id else None
    if not role or role.name.lower() != "writer":
        raise HTTPException(status_code=403, detail="User is not a writer")
    item = models.summary.Summary(
        title=payload.title,
        content=payload.content,
        category_id=payload.category_id,
        writer_id=current_user.user_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.SummaryResponse])
def list_summaries(
    db: Session = Depends(get_db),
    only_writer: bool = Query(True, description="Only summaries created by users with role 'writer'"),
):
    q = db.query(models.summary.Summary)
    if only_writer:
        q = (
            q.join(models.user.User, models.summary.Summary.writer_id == models.user.User.user_id)
             .join(models.user_role.UserRole, models.user.User.role_id == models.user_role.UserRole.role_id)
             .filter(models.user_role.UserRole.name.ilike("writer"))
        )
    return q.all()


@router.get("/{summary_id}", response_model=schema.SummaryResponse)
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    item = db.get(models.summary.Summary, summary_id)
    if not item:
        raise HTTPException(status_code=404, detail="Summary not found")
    return item


@router.put("/{summary_id}", response_model=schema.SummaryResponse)
def update_summary(summary_id: int, payload: schema.SummaryUpdate, db: Session = Depends(get_db)):
    item = db.get(models.summary.Summary, summary_id)
    if not item:
        raise HTTPException(status_code=404, detail="Summary not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{summary_id}")
def delete_summary(summary_id: int, db: Session = Depends(get_db)):
    item = db.get(models.summary.Summary, summary_id)
    if not item:
        raise HTTPException(status_code=404, detail="Summary not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


