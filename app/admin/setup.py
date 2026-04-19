from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import AdminAuthBackend
from app.admin.views import ADMIN_VIEWS
from app.core.config import get_settings
from app.core.db import SessionLocal, engine


def setup_admin(app: FastAPI) -> Admin:
    settings = get_settings()
    auth_backend = AdminAuthBackend(
        secret_key=settings.secret_key,
        session_factory=SessionLocal,
    )
    app.state.admin_auth_backend = auth_backend
    admin = Admin(
        app=app,
        engine=engine,
        title="MyShared Admin",
        base_url="/admin",
        authentication_backend=auth_backend,
    )

    for view in ADMIN_VIEWS:
        admin.add_view(view)

    return admin
