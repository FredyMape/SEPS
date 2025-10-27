from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

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
        server.login(smtp.Username, smtp.PasswordEncrypted)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando al servidor SMTP: {e}")
 
    total = len(group_users)
    sent = 0
    errors = 0
 
    for gu in group_users:
        user = db.query(models.Users).filter(models.Users.Id == gu.UserId).first()
        if not user or not user.Email:
            continue
 
        msg = MIMEMultipart("alternative")
        msg["Subject"] = template.Subject
        msg["From"] = template.EnvelopeSender or smtp.SmtpFrom
        msg["To"] = user.Email
 
        # Cuerpo del correo
        body = MIMEText(template.Content, "html")
        msg.attach(body)
 
        try:
            server.sendmail(msg["From"], msg["To"], msg.as_string())
            sent += 1
 
            # Registrar en CampaignLog
            log = models.CampaignLog(
                CampaignId=campaign.Id,
                UserId=user.Id,
                Email=user.Email,
                Status="Enviado",
                SentAt=datetime.utcnow(),
            )
            db.add(log)
        except Exception as e:
            errors += 1
            log = models.CampaignLog(
                CampaignId=campaign.Id,
                UserId=user.Id,
                Email=user.Email,
                Status=f"Error: {str(e)}",
                SentAt=datetime.utcnow(),
            )
            db.add(log)
 
    db.commit()
    server.quit()
 
    # 6️⃣ Actualizar estado de campaña
    campaign.Status = "Enviada"
    db.commit()
 
    return schemas.LaunchCampaignResult(
        total_recipients=total,
        emails_sent=sent,
        errors=errors,
        message=f"Campaña {campaign.CampaignName} lanzada con éxito" if sent > 0 else "No se enviaron correos"
    )
