from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, database, schemas
 
router = APIRouter(prefix="/landing-pages", tags=["Landing Pages"])
 
@router.post("/")
def create_page(template: schemas.LandingPageBase, db: Session = Depends(database.get_db)):
    page = models.LandingPage(**template.dict())
    db.add(page)
    db.commit()
    db.refresh(page)
    return page
 
@router.get("/")
def get_pages(db: Session = Depends(database.get_db)):
    return db.query(models.LandingPage).all()
 
@router.get("/{id}")
def get_page(id: int, db: Session = Depends(database.get_db)):
    page = db.query(models.LandingPage).filter(models.LandingPage.Id == id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing Page not found")
    return page
 
@router.put("/{id}")
def update_page(id: int, data: schemas.LandingPageBase, db: Session = Depends(database.get_db)):
    page = db.query(models.LandingPage).filter(models.LandingPage.Id == id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing Page not found")
    for k, v in data.dict().items():
        setattr(page, k, v)
    db.commit()
    db.refresh(page)
    return page
 
@router.delete("/{id}")
def delete_page(id: int, db: Session = Depends(database.get_db)):
    page = db.query(models.LandingPage).filter(models.LandingPage.Id == id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing Page not found")
    db.delete(page)
    db.commit()
    return {"message": "Deleted successfully"}
 