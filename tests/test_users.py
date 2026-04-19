class TestUserAPI:
    """用户 API 测试"""

    def test_register_user(self, client):
        """测试用户注册"""
        response = client.post(
            "/users/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

    def test_login_user(self, client):
        """测试用户登录"""
        # 先注册
        client.post(
            "/users/register",
            json={
                "username": "testuser2",
                "email": "test2@example.com",
                "password": "password123"
            }
        )

        # 再登录
        response = client.post(
            "/users/login",
            json={
                "email": "test2@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_invalid_credentials(self, client):
        """测试登录失败"""
        response = client.post(
            "/users/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
