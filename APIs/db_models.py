from datetime import datetime
from sqlalchemy import (
    Integer, String, Text, Boolean, Numeric,
    DateTime, Date, ForeignKey, CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Parent(Base):
    __tablename__ = "parents"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True)
    name:       Mapped[str]      = mapped_column(String(100), nullable=False)
    email:      Mapped[str]      = mapped_column(String(100), unique=True, nullable=False)
    password:   Mapped[str]      = mapped_column(String(255), nullable=False)
    phone:      Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    children:      Mapped[list["Child"]]        = relationship("Child",        back_populates="parent", cascade="all, delete")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="parent", cascade="all, delete")


class Child(Base):
    __tablename__ = "children"

    id:         Mapped[int]        = mapped_column(Integer, primary_key=True)
    parent_id:  Mapped[int]        = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    name:       Mapped[str]        = mapped_column(String(100), nullable=False)
    age:        Mapped[int]        = mapped_column(Integer, nullable=False)
    gender:     Mapped[str | None] = mapped_column(String(10))
    birth_date: Mapped[datetime | None] = mapped_column(Date)
    photo_path: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime]   = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("gender IN ('male','female')", name="chk_gender"),
    )

    parent:   Mapped["Parent"]      = relationship("Parent",  back_populates="children")
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="child", cascade="all, delete")


class Session(Base):
    __tablename__ = "sessions"

    id:                 Mapped[int]      = mapped_column(Integer, primary_key=True)
    child_id:           Mapped[int]      = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), nullable=False)
    detection_type:     Mapped[str]      = mapped_column(String(20), default="initial")
    frames_folder_path: Mapped[str]      = mapped_column(Text, nullable=False)
    detection_date:     Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("detection_type IN ('initial','follow_up')", name="chk_detection_type"),
    )

    child:           Mapped["Child"]            = relationship("Child",          back_populates="sessions")
    analysis_result: Mapped["AnalysisResult | None"] = relationship("AnalysisResult", back_populates="session", uselist=False, cascade="all, delete")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id:               Mapped[int]          = mapped_column(Integer, primary_key=True)
    session_id:       Mapped[int]          = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    risk_level:       Mapped[str | None]   = mapped_column(String(20))
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    analyzed_at:      Mapped[datetime]     = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("risk_level IN ('low','moderate','high')", name="chk_risk_level"),
    )

    session: Mapped["Session"] = relationship("Session", back_populates="analysis_result")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id:                  Mapped[int] = mapped_column(Integer, primary_key=True)
    risk_level:          Mapped[str] = mapped_column(String(20), nullable=False)
    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint("risk_level IN ('low','moderate','high')", name="chk_rec_risk_level"),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True)
    parent_id:  Mapped[int]      = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    title:      Mapped[str]      = mapped_column(String(100), nullable=False)
    message:    Mapped[str]      = mapped_column(Text, nullable=False)
    is_read:    Mapped[bool]     = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    parent: Mapped["Parent"] = relationship("Parent", back_populates="notifications")
