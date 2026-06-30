from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from models.db_models import Parent
from schemas.schemas import LoginRequest, SignupRequest, ParentSessionResponse

router = APIRouter()


# ─── POST /auth/login ─────────────────────────────────────────────────────────
@router.post("/login", response_model=ParentSessionResponse, status_code=200)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate a parent.

    Flutter calls:  POST /auth/login
    Body:           { "email": "...", "password": "..." }
    Returns:        ParentSession  →  { parent_id, name, email, token }
    """
    result = await db.execute(
        select(Parent).where(Parent.email == body.email)
    )
    parent = result.scalar_one_or_none()

    # NOTE: passwords are stored as plain text in the seed data.
    # Replace this check with bcrypt once you add hashing.
    if parent is None or parent.password != body.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return ParentSessionResponse(
        parent_id=str(parent.id),
        name=parent.name,
        email=parent.email,
        token=None,   # add JWT here when you implement auth tokens
    )


# ─── POST /auth/signup ────────────────────────────────────────────────────────
@router.post("/signup", response_model=ParentSessionResponse, status_code=201)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new parent account.

    Flutter calls:  POST /auth/signup
    Body:           { "name": "...", "email": "...", "password": "..." }
    Returns:        ParentSession  →  { parent_id, name, email, token }
    """
    # check if email already exists
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
        password=body.password,   # hash with bcrypt in production
    )
    db.add(new_parent)
    await db.commit()
    await db.refresh(new_parent)

    return ParentSessionResponse(
        parent_id=str(new_parent.id),
        name=new_parent.name,
        email=new_parent.email,
        token=None,
    )
