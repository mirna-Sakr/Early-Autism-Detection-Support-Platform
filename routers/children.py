from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.db_models import Child, Parent, Session, AnalysisResult, Recommendation
from core.schemas import (
    AddChildRequest,
    UpdateChildRequest,
    ChildProfileResponse,
    AssessmentResultResponse,
    BehaviorMetricsResponse,
    RecommendationItem,
    RecommendationsResponse,
)

router = APIRouter()


# ─── helpers ──────────────────────────────────────────────────────────────────

def _child_age(birth_date) -> int:
    if birth_date is None:
        return 0
    today = date.today()
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return max(years, 0)


def _child_to_response(child: Child, last_assessment: str | None = None) -> ChildProfileResponse:
    return ChildProfileResponse(
        id=str(child.id),
        parent_id=str(child.parent_id),
        name=child.name,
        birth_date=child.birth_date.isoformat() if child.birth_date else "",
        age=_child_age(child.birth_date),
        image_url=child.photo_path,
        last_assessment=last_assessment,
    )


# ─── GET /parents/{parent_id}/children ────────────────────────────────────────
@router.get(
    "/parents/{parent_id}/children",
    response_model=list[ChildProfileResponse],
)
async def get_children(parent_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Child).where(Child.parent_id == parent_id)
    )
    children = result.scalars().all()

    response = []
    for child in children:
        sess_result = await db.execute(
            select(Session)
            .where(Session.child_id == child.id)
            .order_by(Session.detection_date.desc())
            .limit(1)
        )
        last_session = sess_result.scalar_one_or_none()
        last_assessment = None
        if last_session:
            ar_result = await db.execute(
                select(AnalysisResult).where(
                    AnalysisResult.session_id == last_session.id
                )
            )
            last_ar = ar_result.scalar_one_or_none()
            if last_ar:
                last_assessment = last_ar.analyzed_at.isoformat()

        response.append(_child_to_response(child, last_assessment))

    return response


# ─── POST /parents/{parent_id}/children ───────────────────────────────────────
@router.post(
    "/parents/{parent_id}/children",
    response_model=ChildProfileResponse,
    status_code=201,
)
async def add_child(
    parent_id: int,
    body: AddChildRequest,
    db: AsyncSession = Depends(get_db),
):
    parent = await db.get(Parent, parent_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="Parent not found")

    birth = datetime.fromisoformat(body.birth_date).date()
    age   = _child_age(birth)

    new_child = Child(
        parent_id=parent_id,
        name=body.name,
        birth_date=birth,
        age=age,
        gender=body.gender,
        photo_path=body.photo_path,
    )
    db.add(new_child)
    await db.commit()
    await db.refresh(new_child)

    return _child_to_response(new_child)


# ─── GET /children/{child_id} ─────────────────────────────────────────────────
@router.get("/children/{child_id}", response_model=ChildProfileResponse)
async def get_child(child_id: int, db: AsyncSession = Depends(get_db)):
    child = await db.get(Child, child_id)
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")
    return _child_to_response(child)


# ─── PUT /children/{child_id} ─────────────────────────────────────────────────
@router.put("/children/{child_id}", response_model=ChildProfileResponse)
async def update_child(
    child_id: int,
    body: UpdateChildRequest,
    db: AsyncSession = Depends(get_db),
):
    child = await db.get(Child, child_id)
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")

    birth            = datetime.fromisoformat(body.birth_date).date()
    child.name       = body.name
    child.birth_date = birth
    child.age        = _child_age(birth)

    await db.commit()
    await db.refresh(child)
    return _child_to_response(child)


# ─── GET /children/{child_id}/assessment ──────────────────────────────────────
@router.get("/children/{child_id}/assessment", response_model=AssessmentResultResponse)
async def get_assessment(child_id: int, db: AsyncSession = Depends(get_db)):
    child = await db.get(Child, child_id)
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")

    sess_result = await db.execute(
        select(Session)
        .where(Session.child_id == child_id)
        .order_by(Session.detection_date.desc())
        .limit(10)
    )
    sessions = sess_result.scalars().all()

    analysis = None
    for sess in sessions:
        ar_result = await db.execute(
            select(AnalysisResult).where(AnalysisResult.session_id == sess.id)
        )
        analysis = ar_result.scalar_one_or_none()
        if analysis:
            break

    if analysis is None:
        raise HTTPException(status_code=404, detail="No assessment found for this child")

    level_map = {"low": 0.2, "moderate": 0.5, "high": 0.8}
    level_val = level_map.get(analysis.risk_level, 0.0)

    return AssessmentResultResponse(
        level=level_val,
        confidence_score=float(analysis.confidence_score) / 100,
        level_label=analysis.risk_level,
        last_updated=analysis.analyzed_at.isoformat(),
    )


# ─── GET /children/{child_id}/behavior ────────────────────────────────────────
@router.get("/children/{child_id}/behavior", response_model=BehaviorMetricsResponse)
async def get_behavior_metrics(child_id: int, db: AsyncSession = Depends(get_db)):
    child = await db.get(Child, child_id)
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")

    sess_result = await db.execute(
        select(Session)
        .where(Session.child_id == child_id)
        .order_by(Session.detection_date.desc())
        .limit(10)
    )
    sessions = sess_result.scalars().all()

    analysis = None
    last_date = None
    for sess in sessions:
        ar_result = await db.execute(
            select(AnalysisResult).where(AnalysisResult.session_id == sess.id)
        )
        analysis = ar_result.scalar_one_or_none()
        if analysis:
            last_date = analysis.analyzed_at
            break

    if analysis is None:
        raise HTTPException(status_code=404, detail="No assessment found for this child")

    behavior_map = {
        "low":      {"eye_contact": 72.0, "social_interaction": 68.0},
        "moderate": {"eye_contact": 45.0, "social_interaction": 40.0},
        "high":     {"eye_contact": 18.0, "social_interaction": 15.0},
    }
    metrics = behavior_map.get(analysis.risk_level, {"eye_contact": 50.0, "social_interaction": 50.0})

    return BehaviorMetricsResponse(
        eye_contact=metrics["eye_contact"],
        social_interaction=metrics["social_interaction"],
        last_updated=last_date.isoformat() if last_date else None,
    )


# ─── GET /children/{child_id}/recommendations ─────────────────────────────────
@router.get("/children/{child_id}/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(child_id: int, db: AsyncSession = Depends(get_db)):
    child = await db.get(Child, child_id)
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")

    sess_result = await db.execute(
        select(Session)
        .where(Session.child_id == child_id)
        .order_by(Session.detection_date.desc())
        .limit(10)
    )
    sessions = sess_result.scalars().all()

    risk_level = None
    for sess in sessions:
        ar = await db.execute(
            select(AnalysisResult).where(AnalysisResult.session_id == sess.id)
        )
        analysis = ar.scalar_one_or_none()
        if analysis:
            risk_level = analysis.risk_level
            break

    if risk_level is None:
        raise HTTPException(status_code=404, detail="No assessment found for this child")

    rec_result = await db.execute(
        select(Recommendation).where(Recommendation.risk_level == risk_level)
    )
    recs = rec_result.scalars().all()

    items = []
    for rec in recs:
        parts = rec.recommendation_text.split(":", 1)
        title = parts[0].strip()
        description = parts[1].strip() if len(parts) > 1 else rec.recommendation_text
        items.append(RecommendationItem(
            id=str(rec.id),
            title=title,
            description=description,
        ))

    return RecommendationsResponse(recommendations=items)