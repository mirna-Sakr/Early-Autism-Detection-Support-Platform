import hashlib
import uuid
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import Assessment, Child, Parent, get_db, init_db

app = FastAPI(title="Early Autism Detection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


def calc_age(birth_date: datetime) -> int:
    today = datetime.utcnow()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return max(age, 0)


def child_to_dict(child: Child, db: Session) -> dict:
    assessment = (
        db.query(Assessment)
        .filter(Assessment.child_id == child.id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    return {
        "id": child.id,
        "parent_id": child.parent_id,
        "name": child.name,
        "birth_date": child.birth_date.isoformat(),
        "age": calc_age(child.birth_date),
        "image_url": child.image_url,
        "last_assessment": child.last_assessment.isoformat()
        if child.last_assessment
        else None,
        "level": assessment.level if assessment else 0.0,
        "confidence_score": assessment.confidence_score if assessment else 0.0,
    }


class ParentSignUp(BaseModel):
    name: str
    email: EmailStr
    password: str


class ParentLogin(BaseModel):
    email: EmailStr
    password: str


class ChildCreate(BaseModel):
    name: str
    birth_date: str


class ChildUpdate(BaseModel):
    name: str | None = None
    birth_date: str | None = None


@app.on_event("startup")
def startup():
    init_db()
    _seed_demo_data()


def _seed_demo_data():
    db = next(get_db())
    try:
        if db.query(Parent).filter(Parent.email == "parent@demo.com").first():
            return

        parent_id = str(uuid.uuid4())
        parent = Parent(
            id=parent_id,
            name="Ahmed Hassan",
            email="parent@demo.com",
            password_hash=hash_password("demo123"),
        )
        db.add(parent)

        children_data = [
            ("CHILD001", "Sara", datetime(2021, 3, 15), 2.5, 0.78, 0.65, 0.45),
            ("CHILD002", "Omar", datetime(2023, 8, 20), 1.8, 0.65, 0.55, 0.40),
        ]
        for cid, name, birth, level, conf, eye, social in children_data:
            child = Child(
                id=cid,
                parent_id=parent_id,
                name=name,
                birth_date=birth,
                last_assessment=datetime.utcnow() - timedelta(days=2),
            )
            db.add(child)
            db.add(
                Assessment(
                    child_id=cid,
                    level=level,
                    confidence_score=conf,
                    eye_contact=eye,
                    social_interaction=social,
                )
            )
        db.commit()
    finally:
        db.close()


RECOMMENDATIONS = [
    {
        "id": "1",
        "title": "Occupational Therapy",
        "description": "Enhances daily living skills, fine motor coordination, and sensory integration.",
    },
    {
        "id": "2",
        "title": "Speech Therapy",
        "description": "Improves verbal and nonverbal communication and language comprehension.",
    },
    {
        "id": "3",
        "title": "Applied Behavior Analysis",
        "description": "Uses data-driven strategies to reinforce positive behaviors.",
    },
    {
        "id": "4",
        "title": "Sensory Integration Therapy",
        "description": "Helps regulate sensory processing and environmental responses.",
    },
    {
        "id": "5",
        "title": "Social Skills Training",
        "description": "Develops interpersonal communication and cooperative play.",
    },
    {
        "id": "6",
        "title": "Special Education Programs",
        "description": "Structured learning tailored to individual needs.",
    },
    {
        "id": "7",
        "title": "Aquatic Therapy",
        "description": "Supports motor development through therapeutic water movement.",
    },
    {
        "id": "8",
        "title": "Art & Music Therapy",
        "description": "Facilitates emotional expression and social engagement.",
    },
]


@app.post("/auth/signup")
def signup(body: ParentSignUp, db: Session = Depends(get_db)):
    if db.query(Parent).filter(Parent.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    parent_id = str(uuid.uuid4())
    parent = Parent(
        id=parent_id,
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(parent)
    db.commit()

    return {
        "parent_id": parent_id,
        "name": parent.name,
        "email": parent.email,
        "token": parent_id,
    }


@app.post("/auth/login")
def login(body: ParentLogin, db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.email == body.email).first()
    if not parent or not verify_password(body.password, parent.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "parent_id": parent.id,
        "name": parent.name,
        "email": parent.email,
        "token": parent.id,
    }


@app.get("/parents/{parent_id}/children")
def list_children(parent_id: str, db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    children = db.query(Child).filter(Child.parent_id == parent_id).all()
    return [child_to_dict(c, db) for c in children]


@app.post("/parents/{parent_id}/children")
def add_child(parent_id: str, body: ChildCreate, db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    child_id = f"CHILD{uuid.uuid4().hex[:6].upper()}"
    birth = datetime.fromisoformat(body.birth_date.replace("Z", ""))
    child = Child(
        id=child_id,
        parent_id=parent_id,
        name=body.name,
        birth_date=birth,
        last_assessment=datetime.utcnow(),
    )
    db.add(child)
    db.add(
        Assessment(
            child_id=child_id,
            level=1.0,
            confidence_score=0.5,
            eye_contact=0.5,
            social_interaction=0.5,
        )
    )
    db.commit()
    db.refresh(child)
    return child_to_dict(child, db)


@app.get("/children/{child_id}")
def get_child(child_id: str, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    return child_to_dict(child, db)


@app.put("/children/{child_id}")
def update_child(child_id: str, body: ChildUpdate, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    if body.name:
        child.name = body.name
    if body.birth_date:
        child.birth_date = datetime.fromisoformat(body.birth_date.replace("Z", ""))

    db.commit()
    db.refresh(child)
    return child_to_dict(child, db)


@app.get("/children/{child_id}/assessment")
def get_assessment(child_id: str, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    assessment = (
        db.query(Assessment)
        .filter(Assessment.child_id == child_id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    if not assessment:
        return {"level": 0.0, "confidence_score": 0.0, "level_label": "Not Assessed"}

    level = assessment.level
    if level < 1.5:
        label = "Needs Support"
    elif level < 2.5:
        label = "Developing"
    elif level < 3.5:
        label = "Progressing Well"
    else:
        label = "On Track"

    return {
        "level": level,
        "confidence_score": assessment.confidence_score,
        "level_label": label,
        "eye_contact": assessment.eye_contact,
        "social_interaction": assessment.social_interaction,
        "last_updated": assessment.created_at.isoformat(),
    }


@app.get("/children/{child_id}/recommendations")
def get_recommendations(child_id: str, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    assessment = (
        db.query(Assessment)
        .filter(Assessment.child_id == child_id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    level = assessment.level if assessment else 1.0

    if level <= 2:
        items = RECOMMENDATIONS[:3]
    elif level <= 3:
        items = RECOMMENDATIONS[:6]
    else:
        items = RECOMMENDATIONS

    return {"level": level, "recommendations": items}


@app.get("/children/{child_id}/notifications/daily")
def daily_reminder(child_id: str, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    return {
        "id": "daily_reminder",
        "title": "Daily Reminder",
        "message": f"Time to check in on {child.name}'s progress today.",
    }
