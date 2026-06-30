from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./autism_detection.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Parent(Base):
    __tablename__ = "parents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    children = relationship("Child", back_populates="parent", cascade="all, delete-orphan")


class Child(Base):
    __tablename__ = "children"

    id = Column(String, primary_key=True, index=True)
    parent_id = Column(String, ForeignKey("parents.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    birth_date = Column(DateTime, nullable=False)
    image_url = Column(String, nullable=True)
    last_assessment = Column(DateTime, nullable=True)

    parent = relationship("Parent", back_populates="children")
    assessments = relationship(
        "Assessment", back_populates="child", cascade="all, delete-orphan"
    )


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(String, ForeignKey("children.id"), nullable=False, index=True)
    level = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    eye_contact = Column(Float, default=0.0)
    social_interaction = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    child = relationship("Child", back_populates="assessments")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
