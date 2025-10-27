from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(prefix="/email-templates", tags=["Email Templates"])

@router.post("/")
def create_template(template: schemas.EmailTemplateBase, db: Session = Depends(database.get_db)):
    new_template = models.EmailTemplate(**template.dict())
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template

@router.get("/")
def get_templates(db: Session = Depends(database.get_db)):
    return db.query(models.EmailTemplate).all()

@router.get("/{id}")
def get_template(id: int, db: Session = Depends(database.get_db)):
    template = db.query(models.EmailTemplate).filter(models.EmailTemplate.Id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/{id}")
def update_template(id: int, updated: schemas.EmailTemplateBase, db: Session = Depends(database.get_db)):
    template = db.query(models.EmailTemplate).filter(models.EmailTemplate.Id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    for k, v in updated.dict().items():
        setattr(template, k, v)
    db.commit()
    db.refresh(template)
    return template

@router.delete("/{id}")
def delete_template(id: int, db: Session = Depends(database.get_db)):
    template = db.query(models.EmailTemplate).filter(models.EmailTemplate.Id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"message": "Deleted successfully"}
