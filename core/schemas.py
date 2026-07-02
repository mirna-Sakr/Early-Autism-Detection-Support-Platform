from __future__ import annotations
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class ParentSessionResponse(BaseModel):
    """Matches Flutter's ParentSession model exactly."""
    parent_id: str
    name: str
    email: str
    token: Optional[str] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# CHILDREN
# ─────────────────────────────────────────────

class AddChildRequest(BaseModel):
    name: str
    birth_date: str           # ISO-8601 string → "2020-05-14T00:00:00.000"
    gender: Optional[str] = None
    photo_path: Optional[str] = None

class UpdateChildRequest(BaseModel):
    name: str
    birth_date: str

class ChildProfileResponse(BaseModel):
    """Matches Flutter's ChildProfile model exactly."""
    id: str
    parent_id: str
    name: str
    birth_date: str
    age: int
    image_url: Optional[str] = None
    last_assessment: Optional[str] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# ASSESSMENT
# ─────────────────────────────────────────────

class AssessmentResultResponse(BaseModel):
    """Matches Flutter's AssessmentResult model exactly."""
    level: float              # numeric risk score 0-1
    confidence_score: float
    level_label: str          # "low" | "moderate" | "high"
    last_updated: Optional[str] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# BEHAVIOR METRICS
# ─────────────────────────────────────────────

class BehaviorMetricsResponse(BaseModel):
    """Matches Flutter's BehaviorMetrics model exactly."""
    eye_contact: float
    social_interaction: float
    last_updated: Optional[str] = None


# ─────────────────────────────────────────────
# RECOMMENDATIONS
# ─────────────────────────────────────────────

class RecommendationItem(BaseModel):
    """Matches Flutter's Recommendation model exactly."""
    id: str
    title: str
    description: str

    model_config = {"from_attributes": True}

class RecommendationsResponse(BaseModel):
    recommendations: List[RecommendationItem]


# ─────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────

class NotificationResponse(BaseModel):
    """Matches Flutter's AppNotification model exactly."""
    id: str
    title: str
    message: str

    model_config = {"from_attributes": True}

class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]


# ─────────────────────────────────────────────
# SESSIONS  (used by IoT module)
# ─────────────────────────────────────────────

class CreateSessionRequest(BaseModel):
    child_id: int
    detection_type: str = "initial"   # "initial" | "follow_up"
    frames_folder_path: str

class SessionResponse(BaseModel):
    id: int
    child_id: int
    detection_type: str
    frames_folder_path: str
    detection_date: str

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# AI RESULT  (called by AI model after inference)
# ─────────────────────────────────────────────

class SaveAnalysisRequest(BaseModel):
    session_id: int
    risk_level: str           # "low" | "moderate" | "high"
    confidence_score: float   # 0.0 – 1.0

class AnalysisResponse(BaseModel):
    id: int
    session_id: int
    risk_level: str
    confidence_score: float
    analyzed_at: str

    model_config = {"from_attributes": True}
