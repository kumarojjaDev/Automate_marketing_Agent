from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Lead(BaseModel):
    lead_id: str
    first_name: str
    last_name: str
    email: str
    linkedin_url: str
    company_name: str
    company_website: str
    role: Optional[str] = None
    intent_score: Optional[float] = None
    status: Optional[str] = None
    status_note: Optional[str] = None
    last_processed_at: Optional[str] = None
    next_action_at: Optional[str] = None
    company_summary: Optional[str] = None
    personal_hook: Optional[str] = None
    angle: Optional[str] = None
    cta: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    email_sent_at: Optional[str] = None
    email_message_id: Optional[str] = None
    linkedin_post: Optional[str] = None
    row_index: int

class CompanyInfo(BaseModel):
    name: str
    industry: Optional[str] = None
    products_services: Optional[str] = None
    mission: Optional[str] = None
    highlights: Optional[str] = None

class LinkedInInfo(BaseModel):
    role: Optional[str] = None
    seniority: Optional[str] = None
    activity_themes: list[str] = Field(default_factory=list)
    recent_post: Optional[str] = None
    about_section: Optional[str] = None
    tone: Optional[str] = None
    verification_level: str = "low"
