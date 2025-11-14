from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, database

router = APIRouter(
    prefix="/smtp-profiles",
    tags=["SMTP Profiles"]
)


# 📨 Crear perfil SMTP
@router.post("/", response_model=schemas.SmtpProfileOut)
def create_profile(
    data: schemas.SmtpProfileCreate,
    db: Session = Depends(database.get_db)
):
    profile = models.SmtpProfile(**data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


# 📋 Obtener todos los perfiles
@router.get("/", response_model=list[schemas.SmtpProfileOut])
def get_profiles(db: Session = Depends(database.get_db)):
    return db.query(models.SmtpProfile).all()


# 🔍 Obtener un perfil por ID
@router.get("/{id}", response_model=schemas.SmtpProfileOut)
def get_profile(id: int, db: Session = Depends(database.get_db)):
    profile = db.query(models.SmtpProfile).filter(models.SmtpProfile.Id == id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="SMTP Profile not found")
    return profile


# ✏️ Actualizar un perfil
@router.put("/{id}", response_model=schemas.SmtpProfileOut)
def update_profile(
    id: int,
    data: schemas.SmtpProfileBase,
    db: Session = Depends(database.get_db)
):
    profile = db.query(models.SmtpProfile).filter(models.SmtpProfile.Id == id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="SMTP Profile not found")

    for key, value in data.model_dump().items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile


# ❌ Eliminar un perfil
@router.delete("/{id}")
def delete_profile(id: int, db: Session = Depends(database.get_db)):
    profile = db.query(models.SmtpProfile).filter(models.SmtpProfile.Id == id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="SMTP Profile not found")

    db.delete(profile)
    db.commit()
    return {"message": "Deleted successfully"}