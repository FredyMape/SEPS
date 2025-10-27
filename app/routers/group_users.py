from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, database, schemas
 
router = APIRouter(prefix="/group-users", tags=["Group Users"])
 
@router.post("/")
def add_user_to_group(data: schemas.GroupUserBase, db: Session = Depends(database.get_db)):
    relation = models.GroupUsers(**data.dict())
    db.add(relation)
    db.commit()
    db.refresh(relation)
    return relation
 
@router.get("/")
def get_relations(db: Session = Depends(database.get_db)):
    return db.query(models.GroupUsers).all()
 
@router.get("/{id}")
def get_relation(id: int, db: Session = Depends(database.get_db)):
    rel = db.query(models.GroupUsers).filter(models.GroupUsers.Id == id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relation not found")
    return rel
 
@router.delete("/{id}")
def delete_relation(id: int, db: Session = Depends(database.get_db)):
    rel = db.query(models.GroupUsers).filter(models.GroupUsers.Id == id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relation not found")
    db.delete(rel)
    db.commit()
    return {"message": "Deleted successfully"}