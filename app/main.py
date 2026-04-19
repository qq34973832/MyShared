from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import app.models  # noqa: F401
from app.admin import setup_admin
from app.core.config import get_settings
from app.core.db import Base, engine
from app.routers import (
    users,
    consumers,
    merchants,
    shared_products,
    ads,
    comments,
    chat,
    webhooks,
    openapi,
    categories,
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

settings = get_settings()

# 创建 FastAPI 应用
app = FastAPI(title="MyShared API", description="多商家电商平台后台系统", version="0.1.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# 注册路由
app.include_router(users.router)
app.include_router(consumers.router)
app.include_router(merchants.router)
app.include_router(shared_products.router)
app.include_router(ads.router)
app.include_router(comments.router)
app.include_router(chat.router)
app.include_router(webhooks.router)
app.include_router(openapi.router)
app.include_router(categories.router)
setup_admin(app)


@app.get("/")
def root():
    """根路由"""
    return {
        "message": "Welcome to MyShared API",
        "docs_url": "/docs",
        "openapi_schema_url": "/openapi.json",
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "Service is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
