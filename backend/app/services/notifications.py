from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Notification, NotificationType, User


class NotificationService:
    async def create_and_send(self, db: AsyncSession, user: User, type_: NotificationType, title: str, body: str, payload: dict | None = None) -> Notification:
        notification = Notification(user_id=user.id, type=type_, title=title, body=body, payload=payload or {}, sent_at=datetime.now(UTC))
        db.add(notification)
        await db.flush()
        # FCM/email providers can be wired here using service-account credentials from env.
        return notification
