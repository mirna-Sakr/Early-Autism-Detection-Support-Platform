from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from db_models import Notification
from schemas import NotificationResponse, NotificationListResponse

router = APIRouter()


# ─── GET /parents/{parent_id}/notifications ───────────────────────────────────
@router.get(
    "/parents/{parent_id}/notifications",
    response_model=NotificationListResponse,
)
async def get_notifications(parent_id: int, db: AsyncSession = Depends(get_db)):
    """Return all notifications for a parent, newest first."""
    result = await db.execute(
        select(Notification)
        .where(Notification.parent_id == parent_id)
        .order_by(Notification.created_at.desc())
    )
    notifications = result.scalars().all()

    return NotificationListResponse(
        notifications=[
            NotificationResponse(
                id=str(n.id),
                title=n.title,
                message=n.message,
            )
            for n in notifications
        ]
    )


# ─── GET /children/{child_id}/notifications/daily ─────────────────────────────
@router.get(
    "/children/{child_id}/notifications/daily",
    response_model=NotificationResponse,
)
async def get_daily_reminder(child_id: int, db: AsyncSession = Depends(get_db)):
    """
    Return the latest unread notification for the parent of this child.
    Flutter calls this endpoint to show the daily reminder card on the dashboard.
    """
    from db_models import Child
    child = await db.get(Child, child_id)
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")

    result = await db.execute(
        select(Notification)
        .where(
            Notification.parent_id == child.parent_id,
            Notification.is_read == False,
        )
        .order_by(Notification.created_at.desc())
        .limit(1)
    )
    notif = result.scalar_one_or_none()

    if notif is None:
        # return a generic reminder if no unread notifications exist
        return NotificationResponse(
            id="0",
            title="Daily Reminder",
            message="Remember to complete today's screening session for your child.",
        )

    return NotificationResponse(
        id=str(notif.id),
        title=notif.title,
        message=notif.message,
    )


# ─── PATCH /notifications/{notification_id}/read ──────────────────────────────
@router.patch("/notifications/{notification_id}/read", status_code=200)
async def mark_as_read(notification_id: int, db: AsyncSession = Depends(get_db)):
    """Mark a notification as read."""
    notif = await db.get(Notification, notification_id)
    if notif is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    await db.commit()
    return {"message": "Notification marked as read"}
