class TestAdAPI:
    """广告 API 测试"""

    def test_create_ad_campaign(self, client):
        """测试创建广告活动"""
        # 注册商家
        client.post(
            "/users/register",
            json={
                "username": "merchant1",
                "email": "merchant@example.com",
                "password": "password123"
            }
        )

        # TODO: 实现完整的广告测试
        pass

    def test_get_ad_analytics(self, client):
        """测试获取广告分析"""
        # TODO: 实现
        pass

    def test_anonymous_ad_pool(self, client):
        """测试匿名广告池"""
        # 注册消费者
        client.post(
            "/users/register",
            json={
                "username": "consumer1",
                "email": "consumer@example.com",
                "password": "password123"
            }
        )

        # 获取 Token
        login_response = client.post(
            "/users/login",
            json={
                "email": "consumer@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]

        # 加入广告池
        response = client.post(
            "/ads/pool/join",
            json={"tags": ["电子产品", "运动"]},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "anonymous_id" in response.json()
