from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .. import models, database, schemas
from datetime import datetime
from pathlib import Path
import app.Utils.fileUtil as fileUtil
 
FILE_PATH = f"{Path(__file__).resolve().parent.parent.parent}\\assets\\templates\\"
 
router = APIRouter(prefix="/landing-pages", tags=["Landing Pages"])
 
@router.post("/")
def create_page(template: schemas.LandingPageBase, db: Session = Depends(database.get_db)):
    try:
        content = template.HtmlContent
        fileName = f"{template.Name.replace(" ", "")}_{datetime.now().strftime("%Y%m%d%H%M%S")}.html"
        template.HtmlContent = fileName
 
        page = models.LandingPage(**template.dict())
        db.add(page)
        db.commit()
        db.refresh(page)
 
        fileUtil.guardar_archivo(FILE_PATH + fileName, content)
        return page
 
    except IntegrityError as e:
            db.rollback()
 
            if "llave duplicada" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un registro con el mismo valor único ({e.orig})"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Error de integridad en la base de datos."
                )
 
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {str(e)}"
        )
 
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
 
@router.get("/")
def get_pages(db: Session = Depends(database.get_db)):
    landingPague = db.query(models.LandingPage).all()

    for page in landingPague:
        page.HtmlContent = fileUtil.leer_archivo(FILE_PATH + page.HtmlContent)
    return landingPague

@router.get("/{id}")
def get_page(id: int, db: Session = Depends(database.get_db)):
    page = db.query(models.LandingPage).filter(models.LandingPage.Id == id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing Page not found")
    return page
 
@router.put("/{id}")
def update_page(id: int, template: schemas.LandingPageBase, db: Session = Depends(database.get_db)):
    
    page = db.query(models.LandingPage).filter(models.LandingPage.Id == id).first()
    try:
        content = template.HtmlContent
        fileName = page.HtmlContent
        template.HtmlContent = fileName

        if not page:
            raise HTTPException(status_code=404, detail="Landing Page not found")
        for k, v in template.dict().items():
            setattr(page, k, v)
        db.commit()
        db.refresh(page)

        fileUtil.guardar_archivo(FILE_PATH + fileName, content)
        page.HtmlContent = fileUtil.leer_archivo(FILE_PATH + fileName)
        return page
    
    except IntegrityError as e:
        db.rollback()

        if "llave duplicada" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un registro con el mismo valor único ({e.orig})"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error de integridad en la base de datos."
                )
 
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {str(e)}"
        )
 
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )

 
@router.delete("/{id}")
def delete_page(id: int, db: Session = Depends(database.get_db)):
    page = db.query(models.LandingPage).filter(models.LandingPage.Id == id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing Page not found")
    db.delete(page)
    db.commit()
    return {"message": "Deleted successfully"}