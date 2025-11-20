from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(prefix="/launch-campaigns", tags=["LaunchCampaigns"])

@router.post("/")
def create_launch_campaign(item: schemas.LaunchCampaignBase, db: Session = Depends(database.get_db)):
    new_item = models.LaunchCampaign(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/")
def get_launch_campaigns(db: Session = Depends(database.get_db)):
    return db.query(models.LaunchCampaign).all()

@router.get("/{id}")
def get_launch_campaign(id: int, db: Session = Depends(database.get_db)):
    item = db.query(models.LaunchCampaign).filter(models.LaunchCampaign.Id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="LaunchCampaign not found")
    return item

@router.put("/{id}")
def update_launch_campaign(id: int, updated: schemas.LaunchCampaignBase, db: Session = Depends(database.get_db)):
    item = db.query(models.LaunchCampaign).filter(models.LaunchCampaign.Id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="LaunchCampaign not found")
    for k, v in updated.dict().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{id}")
def delete_launch_campaign(id: int, db: Session = Depends(database.get_db)):
    item = db.query(models.LaunchCampaign).filter(models.LaunchCampaign.Id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="LaunchCampaign not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted successfully"}