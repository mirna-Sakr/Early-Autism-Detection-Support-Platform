import os
import sys
import json
import tempfile
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import cloudinary
import cloudinary.api
import cloudinary.uploader
import urllib.request

from core.database import get_db, DATABASE_URL
from models.db_models import Session as DBSession, AnalysisResult, Child, Notification
from schemas.schemas import (
    CreateSessionRequest,
    SessionResponse,
    AnalysisResponse,
)

router = APIRouter()

# ─── Cloudinary config ────────────────────────────────────────────────────────
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dsu4nnsrd"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "284865597693164"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "1o8AxBWSvIJCv4F9gIz3v67HTuw"),
    secure=True,
)

# ─── Add AI project to Python path ───────────────────────────────────────────
# الـ Graduation-Project-main folder لازم يكون جنب autism_api على السيرفر
AI_PROJECT_PATH = os.getenv(
    "AI_PROJECT_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "Graduation-Project-main")
)
if AI_PROJECT_PATH not in sys.path:
    sys.path.insert(0, AI_PROJECT_PATH)


# ─── AI Pipeline ──────────────────────────────────────────────────────────────

def download_frames_from_cloudinary(folder_path: str, local_dir: str) -> int:
    """
    يجيب كل الـ frames من Cloudinary folder معين
    ويحفظهم في مجلد مؤقت على السيرفر.
    بيرجع عدد الـ frames اللي اتنزلت.
    """
    # جيب قائمة الـ frames من Cloudinary
    resources = []
    next_cursor = None

    while True:
        kwargs = {
            "type": "upload",
            "prefix": folder_path,
            "max_results": 500,
        }
        if next_cursor:
            kwargs["next_cursor"] = next_cursor

        result = cloudinary.api.resources(**kwargs)
        resources.extend(result.get("resources", []))

        next_cursor = result.get("next_cursor")
        if not next_cursor:
            break

    if not resources:
        return 0

    # نزّل كل frame
    os.makedirs(local_dir, exist_ok=True)
    for res in resources:
        url = res["secure_url"]
        filename = os.path.basename(res["public_id"]) + ".jpg"
        local_path = os.path.join(local_dir, filename)
        urllib.request.urlretrieve(url, local_path)

    return len(resources)


def run_ai_pipeline(frames_local_dir: str) -> dict:
    """
    يشغّل الـ AI pipeline الكاملة على الـ frames:
      1. DeepFace  → emotion features
      2. MediaPipe → pose features
      3. MLP Model → risk_level + confidence
    بيرجع dict فيه risk_level, confidence_score, key_insights
    """
    # Import من الـ Graduation-Project-main
    from emotion_model.extract_sequence import extract_sequence_from_video
    from emotion_model.emotion_features import extract_emotion_features
    from Pose_Detection import process_folder          # pose pipeline
    from fusion_model.inference import predict_from_json

    # ── Step 1: Emotion features ──────────────────────────────
    emotion_seq, conf_seq = extract_sequence_from_video(frames_local_dir)
    emotion_features = extract_emotion_features(emotion_seq, conf_seq)

    # حفظ emotion.json مؤقتاً
    emotion_json_path = os.path.join(frames_local_dir, "_emotion.json")
    with open(emotion_json_path, "w") as f:
        json.dump(emotion_features, f)

    # ── Step 2: Pose features ─────────────────────────────────
    pose_features = process_folder(frames_local_dir)   # بيرجع dict

    # حفظ pose.json مؤقتاً
    pose_json_path = os.path.join(frames_local_dir, "_pose.json")
    with open(pose_json_path, "w") as f:
        json.dump(pose_features, f)

    # ── Step 3: MLP inference ─────────────────────────────────
    result = predict_from_json(emotion_json_path, pose_json_path)

    # تحويل risk_level من High/Medium/Low → high/moderate/low (زي الـ DB)
    level_map = {"High": "high", "Medium": "moderate", "Low": "low"}
    result["risk_level"] = level_map.get(result["risk_level"], "low")

    return result


async def run_analysis_background(session_id: int, frames_folder_path: str, child_id: int):
    """
    الـ Background task الكامل:
      1. ينزّل الـ frames من Cloudinary
      2. يشغّل الـ AI pipeline
      3. يحفظ النتيجة في الـ DB
      4. يبعت notification للأب
    """
    # ─── DB session منفصل للـ background task ────────────────
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # ── 1. نزّل الـ frames في مجلد مؤقت ──────────────
            with tempfile.TemporaryDirectory() as tmp_dir:
                count = download_frames_from_cloudinary(frames_folder_path, tmp_dir)

                if count == 0:
                    print(f"[AI Pipeline] No frames found in: {frames_folder_path}")
                    return

                print(f"[AI Pipeline] Downloaded {count} frames → running analysis...")

                # ── 2. شغّل الـ AI (في thread منفصل عشان مش async) ──
                loop = asyncio.get_event_loop()
                ai_result = await loop.run_in_executor(
                    None,
                    run_ai_pipeline,
                    tmp_dir
                )

            print(f"[AI Pipeline] Result: {ai_result['risk_level']} ({ai_result['risk_score']:.2f})")

            # ── 3. احفظ في الـ DB ─────────────────────────────
            # تأكد مفيش نتيجة قديمة للـ session ده
            existing = await db.execute(
                select(AnalysisResult).where(AnalysisResult.session_id == session_id)
            )
            if existing.scalar_one_or_none():
                print(f"[AI Pipeline] Analysis already exists for session {session_id}")
                return

            analysis = AnalysisResult(
                session_id=session_id,
                risk_level=ai_result["risk_level"],
                confidence_score=round(ai_result["risk_score"] * 100, 2),
            )
            db.add(analysis)

            # ── 4. ابعت notification للأب ─────────────────────
            child = await db.get(Child, child_id)
            if child:
                level_arabic = {
                    "low": "Low Risk ✅",
                    "moderate": "Moderate Risk ⚠️",
                    "high": "High Risk 🔴",
                }.get(ai_result["risk_level"], ai_result["risk_level"])

                notification = Notification(
                    parent_id=child.parent_id,
                    title="Analysis Ready",
                    message=(
                        f"The autism screening analysis for {child.name} "
                        f"has been completed. Risk level: {level_arabic}. "
                        f"Confidence: {round(ai_result['risk_score'] * 100)}%."
                    ),
                )
                db.add(notification)

            await db.commit()
            print(f"[AI Pipeline] ✅ Session {session_id} analysis saved successfully.")

        except Exception as e:
            print(f"[AI Pipeline] ❌ Error in session {session_id}: {e}")
            await db.rollback()

        finally:
            await engine.dispose()


# ─── POST /sessions ───────────────────────────────────────────────────────────
@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(
    body: CreateSessionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    الـ IoT Module بيبعته بعد ما يخلص رفع الـ frames على Cloudinary.

    Body:
      {
        "child_id": 5,
        "detection_type": "initial",
        "frames_folder_path": "Early_Autism_Detection/child_5/session_1"
      }

    الـ API بيعمل:
      1. يحفظ الـ session في الـ DB فوراً ويرجع الـ session_id
      2. في الـ background: ينزّل الـ frames → يشغّل AI → يحفظ النتيجة → يبعت notification
    """
    child = await db.get(Child, body.child_id)
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")

    # حفظ الـ session فوراً
    session = DBSession(
        child_id=body.child_id,
        detection_type=body.detection_type,
        frames_folder_path=body.frames_folder_path,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # شغّل الـ AI في الـ background (مش هيستنى الـ IoT)
    background_tasks.add_task(
        run_analysis_background,
        session.id,
        body.frames_folder_path,
        body.child_id,
    )

    print(f"[Sessions] Session {session.id} created → AI analysis started in background.")

    return SessionResponse(
        id=session.id,
        child_id=session.child_id,
        detection_type=session.detection_type,
        frames_folder_path=session.frames_folder_path,
        detection_date=session.detection_date.isoformat(),
    )


# ─── GET /children/{child_id}/sessions ────────────────────────────────────────
@router.get("/children/{child_id}/sessions", response_model=list[SessionResponse])
async def get_sessions(child_id: int, db: AsyncSession = Depends(get_db)):
    """Return all sessions for a child ordered by newest first."""
    child = await db.get(Child, child_id)
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")

    result = await db.execute(
        select(DBSession)
        .where(DBSession.child_id == child_id)
        .order_by(DBSession.detection_date.desc())
    )
    sessions = result.scalars().all()

    return [
        SessionResponse(
            id=s.id,
            child_id=s.child_id,
            detection_type=s.detection_type,
            frames_folder_path=s.frames_folder_path,
            detection_date=s.detection_date.isoformat(),
        )
        for s in sessions
    ]


# ─── GET /sessions/{session_id}/analysis ──────────────────────────────────────
@router.get("/sessions/{session_id}/analysis", response_model=AnalysisResponse)
async def get_analysis(session_id: int, db: AsyncSession = Depends(get_db)):
    """
    Flutter ممكن تستخدمه لو عايزة تتأكد إن التحليل خلص.
    بترجع 404 لو لسه شغّال في الـ background.
    """
    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.session_id == session_id)
    )
    analysis = result.scalar_one_or_none()

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not ready yet. Please check again in a few moments."
        )

    return AnalysisResponse(
        id=analysis.id,
        session_id=analysis.session_id,
        risk_level=analysis.risk_level,
        confidence_score=float(analysis.confidence_score),
        analyzed_at=analysis.analyzed_at.isoformat(),
    )
