from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.category import Category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
def list_categories(db: Session = Depends(get_db)):
    """获取分类列表"""
    categories = db.query(Category).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "merchant_id": c.merchant_id,
            "parent_id": c.parent_id,
        }
        for c in categories
    ]
