from app.core.security import hash_password
from app.models.user import User, UserRole


class TestAdminConsole:
    def test_admin_requires_login(self, client):
        response = client.get("/admin/", follow_redirects=False)

        assert response.status_code in (302, 307)
        assert "/admin/login" in response.headers["location"]

    def test_admin_login_and_index(self, client):
        register_response = client.post(
            "/users/register",
            json={
                "username": "platform-admin",
                "email": "admin@example.com",
                "password": "password123",
            },
        )
        assert register_response.status_code == 200

        from tests.conftest import TestingSessionLocal

        db = TestingSessionLocal()
        try:
            admin_user = db.query(User).filter(User.email == "admin@example.com").first()
            admin_user.role = UserRole.ADMIN
            admin_user.hashed_password = hash_password("password123")
            db.commit()
        finally:
            db.close()

        login_response = client.post(
            "/admin/login",
            data={"username": "admin@example.com", "password": "password123"},
            follow_redirects=False,
        )

        assert login_response.status_code in (302, 307)

        admin_response = client.get("/admin/", follow_redirects=False)

        assert admin_response.status_code == 200
