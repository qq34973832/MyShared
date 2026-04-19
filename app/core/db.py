from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import get_settings

settings = get_settings()

# 创建引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=NullPool,  # 禁用连接池，适合多进程
)

# 创建 Session 工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
