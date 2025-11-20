from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.Utils.templatesUtils import reemplazar_parametros
from .. import models, schemas, database
import smtplib
import json
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from app.Utils.AesEncript import encrypt_aes256, decrypt_aes256
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="/seps", tags=["Seps"])
password = "f2G9vQ8kzS1aYx7RnbTQeZ_3wLk9u1XhV0pOaC6Bq9I"

@router.post("/")
def create_metric(item: schemas.MetricsBase, db: Session = Depends(database.get_db)):
    new_item = models.Metrics(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/")
def get_metrics(db: Session = Depends(database.get_db)):
    return db.query(models.Metrics).all()

@router.get("/{token}")
def open_campain_file(token: str, db: Session = Depends(database.get_db)):
    plain = decrypt_aes256(token, password)

    if plain is None:
        raise ValueError("Token inválido o desencriptación fallida")
    
    data = json.loads(plain)
    
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL no encontrada en token")

    # redirección (302)
    return RedirectResponse(url=url, status_code=302)

@router.put("/{id}")
def update_metric(id: int, updated: schemas.MetricsBase, db: Session = Depends(database.get_db)):
    item = db.query(models.Metrics).filter(models.Metrics.Id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Metric not found")
    for k, v in updated.dict().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{id}")
def delete_metric(id: int, db: Session = Depends(database.get_db)):
    item = db.query(models.Metrics).filter(models.Metrics.Id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Metric not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted successfully"}