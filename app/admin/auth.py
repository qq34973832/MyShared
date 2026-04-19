from sqlalchemy import or_
from sqladmin.authentication import AuthenticationBackend

from app.core.db import SessionLocal
from app.core.security import verify_password
from app.models.user import User, UserRole


class AdminAuthBackend(AuthenticationBackend):
    def __init__(self, secret_key: str, session_factory=SessionLocal):
        super().__init__(secret_key=secret_key)
        self.session_factory = session_factory

    async def login(self, request) -> bool:
        form = await request.form()
        identifier = (form.get("username") or "").strip()
        password = form.get("password") or ""

        if not identifier or not password:
            return False

        db = self.session_factory()
        try:
            user = db.query(User).filter(
                or_(User.username == identifier, User.email == identifier),
                User.role == UserRole.ADMIN,
            ).first()

            if not user or not verify_password(password, user.hashed_password):
                return False

            if not user.is_active or user.is_banned:
                return False

            request.session.update({"admin_user_id": user.id})
            return True
        finally:
            db.close()

    async def logout(self, request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request) -> bool:
        user_id = request.session.get("admin_user_id")
        if not user_id:
            return False

        db = self.session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return bool(
                user
                and user.role == UserRole.ADMIN
                and user.is_active
                and not user.is_banned
            )
        finally:
            db.close()
