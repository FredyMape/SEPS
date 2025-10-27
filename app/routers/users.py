from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from .. import models, database

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/")
def create_user(template: schemas.UserBase, db: Session = Depends(database.get_db)):
    user = models.Users(**template.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/")
def get_users(db: Session = Depends(database.get_db)):
    return db.query(models.Users).all()

@router.get("/{id}")
def get_user(id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.Users).filter(models.Users.Id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{id}")
def update_user(id: int, template: schemas.UserBase, db: Session = Depends(database.get_db)):
    user = db.query(models.Users).filter(models.Users.Id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for k, v in template.dict().items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{id}")
def delete_user(id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.Users).filter(models.Users.Id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "Deleted successfully"}
