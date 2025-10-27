from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from .. import models, database

router = APIRouter(prefix="/groups", tags=["Groups"])

@router.post("/")
def create_group(template: schemas.GroupBase, db: Session = Depends(database.get_db)):
    group = models.Groups(**template.dict())
    db.add(group)
    db.commit()
    db.refresh(group)
    return group

@router.get("/")
def get_groups(db: Session = Depends(database.get_db)):
    return db.query(models.Groups).all()

@router.get("/{id}")
def get_group(id: int, db: Session = Depends(database.get_db)):
    group = db.query(models.Groups).filter(models.Groups.Id == id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/{id}")
def update_group(id: int, template: schemas.GroupBase, db: Session = Depends(database.get_db)):
    group = db.query(models.Groups).filter(models.Groups.Id == id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    for k, v in template.dict().items():
        setattr(group, k, v)
    db.commit()
    db.refresh(group)
    return group

@router.delete("/{id}")
def delete_group(id: int, db: Session = Depends(database.get_db)):
    group = db.query(models.Groups).filter(models.Groups.Id == id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(group)
    db.commit()
    return {"message": "Deleted successfully"}
