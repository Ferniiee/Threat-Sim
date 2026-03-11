from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models import Campaign, AuditLog
from pydantic import BaseModel
from typing import Optional
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

router = APIRouter(prefix="/campaigns", tags=["campaigns"])
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        role = payload.get("role")
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

class CampaignCreate(BaseModel):
    name: str
    subject: str
    body: str
    campaign_type: str

class CampaignUpdate(BaseModel):
    status: Optional[str] = None
    name: Optional[str] = None

def campaign_to_dict(c):
    return {
        "id": c.id,
        "name": c.name,
        "subject": c.subject,
        "body": c.body,
        "campaign_type": c.campaign_type,
        "status": c.status,
        "created_by": c.created_by,
        "created_at": str(c.created_at)
    }

@router.post("/")
def create_campaign(
    req: CampaignCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    campaign = Campaign(
        name=req.name,
        subject=req.subject,
        body=req.body,
        campaign_type=req.campaign_type,
        created_by=current_user["user_id"]
    )
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    log = AuditLog(
        user_id=current_user["user_id"],
        action="campaign_created",
        detail="Campaign created by user " + str(current_user["user_id"])
    )
    session.add(log)
    session.commit()
    return campaign_to_dict(campaign)

@router.get("/")
def list_campaigns(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    campaigns = session.exec(select(Campaign)).all()
    return [campaign_to_dict(c) for c in campaigns]

@router.get("/{campaign_id}")
def get_campaign(
    campaign_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign_to_dict(campaign)

@router.patch("/{campaign_id}")
def update_campaign(
    campaign_id: int,
    req: CampaignUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if req.status:
        campaign.status = req.status
    if req.name:
        campaign.name = req.name
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    log = AuditLog(
        user_id=current_user["user_id"],
        action="campaign_updated",
        detail="Campaign " + str(campaign_id) + " updated"
    )
    session.add(log)
    session.commit()
    return campaign_to_dict(campaign)