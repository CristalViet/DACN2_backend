from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import publisher as schema
from app.core.deps import require_admin

router = APIRouter(prefix="/publishers", tags=["Publishers"])


@router.post("/", response_model=schema.PublisherResponse)
def create_publisher(
    payload: schema.PublisherCreate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new publisher (Admin only)"""
    item = models.publisher.Publisher(name=payload.name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[schema.PublisherResponse])
def list_publishers(db: Session = Depends(get_db)):
    """Get all publishers (Public access)"""
    return db.query(models.publisher.Publisher).all()


@router.get("/{publisher_id}", response_model=schema.PublisherResponse)
def get_publisher(publisher_id: int, db: Session = Depends(get_db)):
    """Get a specific publisher (Public access)"""
    item = db.get(models.publisher.Publisher, publisher_id)
    if not item:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return item


@router.put("/{publisher_id}", response_model=schema.PublisherResponse)
def update_publisher(
    publisher_id: int,
    payload: schema.PublisherUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a publisher (Admin only)"""
    item = db.get(models.publisher.Publisher, publisher_id)
    if not item:
        raise HTTPException(status_code=404, detail="Publisher not found")
    if payload.name is not None:
        item.name = payload.name
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{publisher_id}")
def delete_publisher(
    publisher_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a publisher (Admin only)"""
    item = db.get(models.publisher.Publisher, publisher_id)
    if not item:
        raise HTTPException(status_code=404, detail="Publisher not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}

