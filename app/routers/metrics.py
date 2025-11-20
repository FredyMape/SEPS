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
    
    item = db.query(models.Metrics).filter(models.Metrics.IdLaunch == data.get("launch_id"), models.Metrics.IdUser == data.get("user_id")).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    metrics_object = schemas.MetricsCreate(
        IdLaunch = data.get("launch_id"),
        IdUser = data.get("user_id"),
        SendMail= item.SendMail,
        OpenMail = item.OpenMail,
        OpenLandingPage = item.OpenLandingPage,
        SendData = item.SendData,
        TrainingCompleted = item.TrainingCompleted
    )

    token_data = token

    if data.get("metric") == "open_landing_page":   
        metrics_object.OpenMail = True
        metrics_object.OpenLandingPage = True

        new_data = {
            "user_id":  data.get("user_id"),
            "url": "http://44.216.31.216:80/pages/Training.html",
            "launch_id": data.get("launch_id"),
            "metric": "send_data",
        }

        token_data = encrypt_aes256(json.dumps(new_data, ensure_ascii=False, indent=2), password)

    if data.get("metric") == "send_data":   
        metrics_object.SendData = True 

        new_data = {
            "user_id":  data.get("user_id"),
            "url": "http://44.216.31.216:80/pages/Training.html",
            "launch_id": data.get("launch_id"),
            "metric": "training_completed",
        }

        token_data = encrypt_aes256(json.dumps(new_data, ensure_ascii=False, indent=2), password)

    if data.get("metric") == "training_completed":
        metrics_object.TrainingCompleted = True 
    
    
    for k, v in metrics_object.dict().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)

    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL no encontrada en token")

    # redirección (302)
    return RedirectResponse(url=url + '?p=' + urllib.parse.quote(token_data, safe=''), status_code=302)

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