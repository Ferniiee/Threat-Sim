from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# --- USER TABLE ---
# Admins who log in and run campaigns
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: str = Field(default="admin")  # "admin" or "viewer"
    created_at: datetime = Field(default_factory=datetime.utcnow)


# --- CAMPAIGN TABLE ---
# A phishing simulation campaign (e.g. "Q1 Credential Harvest Test")
class Campaign(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    subject: str                    # Email subject line
    body: str                       # Email body (supports {{first_name}} variables)
    campaign_type: str              # "credential-harvest", "urgency", "attachment-lure"
    status: str = Field(default="draft")  # draft → active → completed
    created_by: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# --- TARGET TABLE ---
# An employee being tested in a campaign
class Target(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaign.id")
    first_name: str
    last_name: str
    email: str
    department: str
    # This is the UUID that makes our tracking system work
    # Every target gets a unique one - no two are ever the same
    tracking_uuid: str = Field(default_factory=generate_uuid, unique=True, index=True)
    training_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# --- TRACKING EVENT TABLE ---
# Every interaction (open, click, report) gets logged here
# This table is NEVER updated or deleted - only inserted (immutable log)
class TrackingEvent(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    tracking_uuid: str = Field(index=True)  # links back to Target
    event_type: str        # "open", "click", "report"
    ip_address: str
    user_agent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- AUDIT LOG TABLE ---
# Immutable record of every admin action in the system (SOC2 pattern)
class AuditLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None)
    action: str            # e.g. "campaign_created", "user_login"
    detail: str            # e.g. "Campaign ID 3 created by admin@test.com"
    timestamp: datetime = Field(default_factory=datetime.utcnow)