from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models,schemas, database

router = APIRouter(prefix="/smtp-profiles", tags=["SMTP Profiles"])

@router.post("/", response_model=schemas.SmtpProfileOut)
def create_profile(data: schemas.SmtpProfileCreate, db: Session = Depends(database.get_db)):
    profile = models.SmtpProfile(**data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/")
def get_profiles(db: Session = Depends(database.get_db)):
    return db.query(models.SmtpProfile).all()

@router.get("/{id}")
def get_profile(id: int, db: Session = Depends(database.get_db)):
    profile = db.query(models.SmtpProfile).filter(models.SmtpProfile.Id == id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="SMTP Profile not found")
    return profile

@router.put("/{id}", response_model=schemas.SmtpProfileBase)
def update_profile(id: int, data: schemas.SmtpProfileBase, db: Session = Depends(database.get_db)):
    profile = db.query(models.SmtpProfile).filter(models.SmtpProfile.Id == id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="SMTP Profile not found")
    for k, v in data.dict().items():
        setattr(profile, k, v)
    db.commit()
    db.refresh(profile)
    return profile

@router.delete("/{id}")
def delete_profile(id: int, db: Session = Depends(database.get_db)):
    profile = db.query(models.SmtpProfile).filter(models.SmtpProfile.Id == id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="SMTP Profile not found")
    db.delete(profile)
    db.commit()
    return {"message": "Deleted successfully"}