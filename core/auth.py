from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt
from datetime import datetime, timedelta

from core.database import get_db
from core.db_models import Parent
from core.schemas import LoginRequest, SignupRequest, ParentSessionResponse

router = APIRouter()

SECRET_KEY = "autism-detection-secret-2024"
ALGORITHM = "HS256"

def create_token(parent_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": parent_id, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ─── POST /auth/login ─────────────────────────────────────────────────────────
@router.post("/login", response_model=ParentSessionResponse, status_code=200)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Parent).where(Parent.email == body.email)
    )
    parent = result.scalar_one_or_none()

    if parent is None or parent.password != body.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return ParentSessionResponse(
        parent_id=str(parent.id),
        name=parent.name,
        email=parent.email,
        token=create_token(str(parent.id)),
    )


# ─── POST /auth/signup ────────────────────────────────────────────────────────
@router.post("/signup", response_model=ParentSessionResponse, status_code=201)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Parent).where(Parent.email == body.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    new_parent = Parent(
        name=body.name,
        email=body.email,
        password=body.password,
    )
    db.add(new_parent)
    await db.commit()
    await db.refresh(new_parent)

    return ParentSessionResponse(
        parent_id=str(new_parent.id),
        name=new_parent.name,
        email=new_parent.email,
        token=create_token(str(new_parent.id)),
    )