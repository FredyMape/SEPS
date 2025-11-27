from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.Utils.templatesUtils import reemplazar_parametros
from .. import models, schemas, database
import smtplib
import json
import urllib.parse
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from app.Utils.AesEncript import encrypt_aes256

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])
password = "f2G9vQ8kzS1aYx7RnbTQeZ_3wLk9u1XhV0pOaC6Bq9I"

@router.post("/")
def create_campaign(template: schemas.CampaignBase, db: Session = Depends(database.get_db)):
    campaign = models.Campaign(**template.dict())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign

@router.get("/")
def get_campaigns(db: Session = Depends(database.get_db)):
    return db.query(models.Campaign).all()

@router.get("/{id}")
def get_campaign(id: int, db: Session = Depends(database.get_db)):
    campaign = db.query(models.Campaign).filter(models.Campaign.Id == id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.put("/{id}")
def update_campaign(id: int, template: schemas.CampaignBase, db: Session = Depends(database.get_db)):
    campaign = db.query(models.Campaign).filter(models.Campaign.Id == id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for k, v in template.dict().items():
        setattr(campaign, k, v)
    db.commit()
    db.refresh(campaign)
    return campaign

@router.delete("/{id}")
def delete_campaign(id: int, db: Session = Depends(database.get_db)):
    campaign = db.query(models.Campaign).filter(models.Campaign.Id == id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    db.delete(campaign)
    db.commit()
    return {"message": "Deleted successfully"}

@router.post("/launch/{id}")
def launch_campaign(id: int, db: Session = Depends(database.get_db)):
    
    
    # 1️⃣ Obtener campaña
    campaign = db.query(models.Campaign).filter(models.Campaign.Id == id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
 
    # 2️⃣ Obtener plantilla de correo
    template = db.query(models.EmailTemplate).filter(models.EmailTemplate.Id == campaign.EmailTemplateId).first()
    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
 
    # 3️⃣ Obtener configuración SMTP
    smtp = db.query(models.SmtpProfile).filter(models.SmtpProfile.Id == campaign.SmtpProfileId).first()
    if not smtp:
        raise HTTPException(status_code=404, detail="Perfil SMTP no encontrado")
 
    # Obtener landing page
    landing_page = db.query(models.LandingPage).filter(models.LandingPage.Id == campaign.LandingPageId).first()
    if not landing_page:
        raise HTTPException(status_code=404, detail="Perfil SMTP no encontrado")
    
    # 4️⃣ Obtener usuarios del grupo
    group_users = (
        db.query(models.GroupUsers)
        .filter(models.GroupUsers.GroupId == campaign.GroupId)
        .join(models.Users, models.Users.Id == models.GroupUsers.UserId)
        .filter(models.Users.IsActive == True)
        .all()
    )
 
    if not group_users:
        raise HTTPException(status_code=400, detail="No hay usuarios activos en el grupo asociado")
 
    # 5️⃣ Configurar servidor SMTP
    try:
        server = smtplib.SMTP(smtp.Host, smtp.Port)
        if smtp.UseTls:
            server.starttls()
        server.login(smtp.Username, "jzhf ytvj atci nxez")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando al servidor SMTP: {e}")
 
    total = len(group_users)
    sent = 0
    errors = 0
 
    launch = schemas.LaunchCampaignBase(
        IdCampaign = campaign.Id,
        Date = datetime.utcnow(),
        TotalRecipients = 0,
        EmailsSent = 0
    )

    launch_campain = models.LaunchCampaign(**launch.dict())
    db.add(launch_campain)
    db.commit()
    db.refresh(launch_campain)

    for gu in group_users:
        user = db.query(models.Users).filter(models.Users.Id == gu.UserId).first()
        if not user or not user.Email:
            continue
        
        fecha_actual = datetime.now() + timedelta(hours=5)

        data = {
            "user_id": user.Id,
            "url": "http://44.216.31.216:80/pages/" + landing_page.HtmlContent,
            "launch_id": launch_campain.Id,
            "metric": "open_landing_page",
        }

        token_data = encrypt_aes256(json.dumps(data, ensure_ascii=False, indent=2), password)

        parametros = {
            "NOMBRE_USUARIO": (user.FirstName or "") + " " + (user.MiddleName or ""),
            "FECHA_EXPIRACION": fecha_actual.strftime("%d/%m/%Y"),
            "URL_HREF": "http://44.216.31.216:80/seps/" +  urllib.parse.quote(token_data, safe='')
        }


        email_content = template.Content
        email_content = reemplazar_parametros(email_content, parametros)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = template.Subject

        sender_name = template.EnvelopeSender
        sender_email = smtp.SmtpFrom

        msg["From"] = f"{sender_name} <{sender_email}>"
        msg["To"] = user.Email
 
        # Cuerpo del correo
        body = MIMEText(email_content, "html")
        msg.attach(body)
 
        metrics_object = schemas.MetricsCreate(
            IdLaunch = launch_campain.Id,
            IdUser = user.Id,
            SendMail = True
        )

        try:
            server.sendmail(msg["From"], msg["To"], msg.as_string())
            sent += 1
 
            metrics = models.Metrics(**metrics_object.dict())
            db.add(metrics)
            db.commit()
            db.refresh(metrics)
            
            time.sleep(3)

            # Registrar en CampaignLog
            # log = models.CampaignLog(
            #     CampaignId=campaign.Id,
            #     UserId=user.Id,
            #     Email=user.Email,
            #     Status="Enviado",
            #     SentAt=datetime.utcnow(),
            # )
            # db.add(log)
        except Exception as e:
            errors += 1

            metrics_object.SendMail = False
            metrics = models.Metrics(**metrics_object.dict())
            db.add(metrics)
            db.commit()
            db.refresh(metrics)

            time.sleep(3)

            # log = models.CampaignLog(
            #     CampaignId=campaign.Id,
            #     UserId=user.Id,
            #     Email=user.Email,
            #     Status=f"Error: {str(e)}",
            #     SentAt=datetime.utcnow(),
            # )
            # db.add(log)
 
    db.commit()
    server.quit()
 
    # 6️⃣ Actualizar estado de campaña
    campaign.Status = "Enviada"
    db.commit()
 
    # 7 Actualizar metricas de campaña
    launch.TotalRecipients = total
    launch.EmailsSent = sent

    for k, v in launch.dict().items():
        setattr(launch_campain, k, v)
    db.commit()
    db.refresh(launch_campain)

    

    return schemas.LaunchCampaignResult(
        total_recipients = total,
        emails_sent = sent,
        errors = errors,
        message = f"Campaña {campaign.CampaignName} lanzada con éxito" if sent > 0 else "No se enviaron correos"
    )
