from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import AdminAuthBackend
from app.admin.views import ADMIN_VIEWS
from app.core.config import get_settings
from app.core.db import engine


def setup_admin(app: FastAPI) -> Admin:
    settings = get_settings()
    admin = Admin(
        app=app,
        engine=engine,
        title="MyShared Admin",
        base_url="/admin",
        authentication_backend=AdminAuthBackend(secret_key=settings.secret_key),
    )

    for view in ADMIN_VIEWS:
        admin.add_view(view)

    return admin
