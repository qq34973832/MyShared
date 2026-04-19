from datetime import datetime, timedelta, timezone

from sqlalchemy import or_

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.ad_campaign import AdCampaign
from app.models.api_token import APIToken
from app.models.category import Category
from app.models.comment import Comment
from app.models.consumer import ConsumerProfile
from app.models.merchant import Merchant
from app.models.shared_product import SharedProduct, Bid
from app.models.subscription import Subscription
from app.models.user import User, UserRole, UserPermission
from app.models.webhook import Webhook


def seed_initial_data() -> None:
    settings = get_settings()
    if not settings.auto_seed_data:
        return

    db = SessionLocal()
    try:
        # === Admin 用户 ===
        admin_user = (
            db.query(User)
            .filter(or_(User.username == "admin", User.email == "admin@example.com"))
            .first()
        )
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("1234"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin_user)

        # === Alice - 普通消费者 ===
        alice_user = (
            db.query(User)
            .filter(or_(User.username == "alice", User.email == "alice@example.com"))
            .first()
        )
        if not alice_user:
            alice_user = User(
                username="alice",
                email="alice@example.com",
                hashed_password=hash_password("1234"),
                role=UserRole.CONSUMER,
                is_active=True,
            )
            db.add(alice_user)

        # === Lily - 商户 ===
        lily_user = (
            db.query(User)
            .filter(or_(User.username == "lily", User.email == "lily@example.com"))
            .first()
        )
        if not lily_user:
            lily_user = User(
                username="lily",
                email="lily@example.com",
                hashed_password=hash_password("1234"),
                role=UserRole.MERCHANT,
                is_active=True,
            )
            db.add(lily_user)

        # === 旧演示用户（保持兼容） ===
        merchant_user = (
            db.query(User)
            .filter(
                or_(
                    User.username == "merchant-demo",
                    User.email == "merchant@example.com",
                )
            )
            .first()
        )
        if not merchant_user:
            merchant_user = User(
                username="merchant-demo",
                email="merchant@example.com",
                hashed_password=hash_password("123456"),
                role=UserRole.MERCHANT,
                is_active=True,
            )
            db.add(merchant_user)

        consumer_user = (
            db.query(User)
            .filter(
                or_(
                    User.username == "consumer-demo",
                    User.email == "consumer@example.com",
                )
            )
            .first()
        )
        if not consumer_user:
            consumer_user = User(
                username="consumer-demo",
                email="consumer@example.com",
                hashed_password=hash_password("123456"),
                role=UserRole.CONSUMER,
                is_active=True,
            )
            db.add(consumer_user)

        db.commit()
        db.refresh(admin_user)
        db.refresh(alice_user)
        db.refresh(lily_user)
        db.refresh(merchant_user)
        db.refresh(consumer_user)

        # === 用户权限 ===
        for perm in ["user:read", "user:write", "product:read", "product:write", "admin:all"]:
            exists = db.query(UserPermission).filter(
                UserPermission.user_id == admin_user.id,
                UserPermission.permission == perm,
            ).first()
            if not exists:
                db.add(UserPermission(user_id=admin_user.id, permission=perm))

        for perm in ["product:read", "order:read"]:
            exists = db.query(UserPermission).filter(
                UserPermission.user_id == alice_user.id,
                UserPermission.permission == perm,
            ).first()
            if not exists:
                db.add(UserPermission(user_id=alice_user.id, permission=perm))

        # === 消费者档案 ===
        alice_profile = (
            db.query(ConsumerProfile)
            .filter(ConsumerProfile.user_id == alice_user.id)
            .first()
        )
        if not alice_profile:
            alice_profile = ConsumerProfile(
                user_id=alice_user.id,
                nickname="Alice",
                tags=["美妆", "时尚", "家居"],
                preferences={"language": "zh-CN", "currency": "CNY"},
            )
            db.add(alice_profile)

        consumer_profile = (
            db.query(ConsumerProfile)
            .filter(ConsumerProfile.user_id == consumer_user.id)
            .first()
        )
        if not consumer_profile:
            consumer_profile = ConsumerProfile(
                user_id=consumer_user.id,
                nickname="演示消费者",
                tags=["数码", "家居"],
                preferences={"language": "zh-CN", "currency": "CNY"},
            )
            db.add(consumer_profile)

        db.commit()

        # === 商户档案 ===
        lily_merchant = db.query(Merchant).filter(Merchant.user_id == lily_user.id).first()
        if not lily_merchant:
            lily_merchant = Merchant(
                user_id=lily_user.id,
                shop_name="Lily的美妆小铺",
                shop_description="专注高品质美妆产品，正品保证",
                contact_phone="13900001111",
                contact_email="lily@example.com",
                address="Shanghai",
                is_verified=True,
                total_products=3,
                rating=5,
                total_reviews=8,
            )
            db.add(lily_merchant)

        merchant = db.query(Merchant).filter(Merchant.user_id == merchant_user.id).first()
        if not merchant:
            merchant = Merchant(
                user_id=merchant_user.id,
                shop_name="演示共享店铺",
                shop_description="用于本地联调和演示的默认店铺",
                contact_phone="13800000000",
                contact_email="merchant@example.com",
                address="Hangzhou",
                is_verified=True,
                total_products=2,
                rating=5,
                total_reviews=1,
            )
            db.add(merchant)

        db.commit()
        db.refresh(lily_merchant)
        db.refresh(merchant)

        # === 商品分类 ===
        category = db.query(Category).filter(Category.slug == "demo-electronics").first()
        if not category:
            category = Category(
                merchant_id=merchant.id,
                name="演示数码",
                slug="demo-electronics",
                description="默认测试分类",
                sort_order=1,
            )
            db.add(category)

        beauty_cat = db.query(Category).filter(Category.slug == "beauty").first()
        if not beauty_cat:
            beauty_cat = Category(
                merchant_id=lily_merchant.id,
                name="美妆护肤",
                slug="beauty",
                description="美妆护肤产品分类",
                sort_order=1,
            )
            db.add(beauty_cat)

        fashion_cat = db.query(Category).filter(Category.slug == "fashion").first()
        if not fashion_cat:
            fashion_cat = Category(
                merchant_id=lily_merchant.id,
                name="时尚配饰",
                slug="fashion",
                description="时尚配饰类产品",
                sort_order=2,
            )
            db.add(fashion_cat)

        db.commit()
        db.refresh(category)
        db.refresh(beauty_cat)
        db.refresh(fashion_cat)

        # === 商品 ===
        product = db.query(SharedProduct).filter(SharedProduct.name == "演示蓝牙耳机").first()
        if not product:
            product = SharedProduct(
                merchant_id=merchant.id,
                category_id=category.id,
                name="演示蓝牙耳机",
                sku="DEMO-HEADSET-001",
                description="默认测试商品，可直接用于接口联调",
                image_urls=["https://example.com/demo-headset.png"],
                original_price=199.0,
                current_price=149.0,
                min_platform_price=139.0,
                stock=50,
                is_available=True,
                sales_count=12,
                rating=4.8,
                review_count=1,
                metadata_={"seeded": True},
            )
            db.add(product)

        product2 = db.query(SharedProduct).filter(SharedProduct.name == "精华液套装").first()
        if not product2:
            product2 = SharedProduct(
                merchant_id=lily_merchant.id,
                category_id=beauty_cat.id,
                name="精华液套装",
                sku="LILY-BEAUTY-001",
                description="补水保湿精华液三件套，适合干性/混合性肌肤",
                image_urls=["https://example.com/serum-set.png"],
                original_price=299.0,
                current_price=239.0,
                min_platform_price=219.0,
                stock=100,
                is_available=True,
                sales_count=56,
                rating=4.9,
                review_count=8,
                metadata_={"seeded": True},
            )
            db.add(product2)

        product3 = db.query(SharedProduct).filter(SharedProduct.name == "复古太阳镜").first()
        if not product3:
            product3 = SharedProduct(
                merchant_id=lily_merchant.id,
                category_id=fashion_cat.id,
                name="复古太阳镜",
                sku="LILY-FASHION-001",
                description="经典复古风格偏光太阳镜，UV400防护",
                image_urls=["https://example.com/sunglasses.png"],
                original_price=159.0,
                current_price=119.0,
                min_platform_price=99.0,
                stock=200,
                is_available=True,
                sales_count=33,
                rating=4.6,
                review_count=5,
                metadata_={"seeded": True},
            )
            db.add(product3)

        db.commit()
        db.refresh(product)
        db.refresh(product2)
        db.refresh(product3)

        # === 竞价 ===
        bid_exists = db.query(Bid).filter(
            Bid.product_id == product2.id, Bid.merchant_id == merchant.id
        ).first()
        if not bid_exists:
            db.add(Bid(
                product_id=product2.id,
                merchant_id=merchant.id,
                bid_price=229.0,
                status="active",
                bid_amount=500.0,
            ))

        # === 广告活动 ===
        campaign = db.query(AdCampaign).filter(AdCampaign.name == "默认演示广告").first()
        if not campaign:
            now = datetime.now(timezone.utc)
            campaign = AdCampaign(
                merchant_id=merchant.id,
                name="默认演示广告",
                description="用于广告接口演示的默认活动",
                target_tags=["数码", "耳机"],
                daily_budget=100.0,
                total_budget=500.0,
                spent_budget=0.0,
                start_date=now,
                end_date=now + timedelta(days=30),
                status="active",
                is_active=True,
            )
            db.add(campaign)

        lily_campaign = db.query(AdCampaign).filter(AdCampaign.name == "美妆新品推广").first()
        if not lily_campaign:
            now = datetime.now(timezone.utc)
            lily_campaign = AdCampaign(
                merchant_id=lily_merchant.id,
                name="美妆新品推广",
                description="精华液套装新品上市推广活动",
                target_tags=["美妆", "护肤", "女性"],
                daily_budget=200.0,
                total_budget=1000.0,
                spent_budget=50.0,
                start_date=now,
                end_date=now + timedelta(days=15),
                status="active",
                is_active=True,
            )
            db.add(lily_campaign)

        # === 评论 ===
        if alice_user:
            db.refresh(alice_profile)
            comment_exists = (
                db.query(Comment)
                .filter(Comment.user_id == alice_user.id, Comment.product_id == product2.id)
                .first()
            )
            if not comment_exists:
                db.add(Comment(
                    user_id=alice_user.id,
                    product_id=product2.id,
                    merchant_id=lily_merchant.id,
                    rating=5,
                    title="非常好用！",
                    content="用了一周，皮肤明显变好了，补水效果很棒，推荐！",
                    helpful_count=10,
                    unhelpful_count=0,
                    is_verified_purchase=1,
                ))

        comment_exists = (
            db.query(Comment)
            .filter(Comment.user_id == consumer_user.id, Comment.product_id == product.id)
            .first()
        )
        if not comment_exists:
            db.add(Comment(
                user_id=consumer_user.id,
                product_id=product.id,
                merchant_id=merchant.id,
                rating=5,
                title="默认演示评价",
                content="这是一条自动填充的测试评价，用于验证评论管理页面。",
                helpful_count=3,
                unhelpful_count=0,
                is_verified_purchase=1,
            ))

        # === 订阅 ===
        if alice_profile:
            sub_exists = db.query(Subscription).filter(
                Subscription.consumer_id == alice_profile.id,
                Subscription.merchant_id == lily_merchant.id,
            ).first()
            if not sub_exists:
                db.add(Subscription(
                    consumer_id=alice_profile.id,
                    merchant_id=lily_merchant.id,
                    subscription_type="merchant",
                    is_active=True,
                ))

        # === Webhook ===
        wh = db.query(Webhook).filter(Webhook.name == "测试Webhook").first()
        if not wh:
            db.add(Webhook(
                name="测试Webhook",
                url="https://example.com/webhook/receive",
                events=["user.created", "order.paid", "product.updated"],
                secret="webhook-test-secret-key",
                is_active=True,
            ))

        # === API Token ===
        token_exists = db.query(APIToken).filter(APIToken.name == "admin-test-token").first()
        if not token_exists:
            db.add(APIToken(
                user_id=admin_user.id,
                token="sk-test-admin-token-000000000001",
                name="admin-test-token",
                scopes=["user:read", "user:write", "product:read", "product:write"],
                is_active=True,
                is_revoked=False,
            ))

        db.commit()
    finally:
        db.close()
