from datetime import datetime, timedelta, timezone

from sqlalchemy import or_

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.ad_campaign import AdCampaign
from app.models.category import Category
from app.models.comment import Comment
from app.models.consumer import ConsumerProfile
from app.models.merchant import Merchant
from app.models.shared_product import SharedProduct
from app.models.user import User, UserRole


def seed_initial_data() -> None:
    settings = get_settings()
    if not settings.auto_seed_data:
        return

    db = SessionLocal()
    try:
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
        db.refresh(merchant_user)
        db.refresh(consumer_user)

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
                total_products=1,
                rating=5,
                total_reviews=1,
            )
            db.add(merchant)
            db.commit()
            db.refresh(merchant)

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
            db.commit()
            db.refresh(category)

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
            db.commit()
            db.refresh(product)

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

        comment_exists = (
            db.query(Comment)
            .filter(Comment.user_id == consumer_user.id, Comment.product_id == product.id)
            .first()
        )
        if not comment_exists:
            db.add(
                Comment(
                    user_id=consumer_user.id,
                    product_id=product.id,
                    merchant_id=merchant.id,
                    rating=5,
                    title="默认演示评价",
                    content="这是一条自动填充的测试评价，用于验证评论管理页面。",
                    helpful_count=3,
                    unhelpful_count=0,
                    is_verified_purchase=1,
                )
            )

        db.commit()
    finally:
        db.close()
