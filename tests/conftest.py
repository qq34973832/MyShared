import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.db import Base
import app.models  # noqa: F401

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.db import get_db

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.state.admin_auth_backend.session_factory = TestingSessionLocal
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
