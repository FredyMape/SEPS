from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, database

router = APIRouter(prefix="/campaign-recipients", tags=["Campaign Recipients"])

@router.get("/")
def get_recipients(db: Session = Depends(database.get_db)):
    return db.query(models.vw_CampaignRecipients).all()
