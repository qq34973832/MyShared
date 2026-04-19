from fastapi import APIRouter

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
def list_categories():
    """获取分类列表"""
    pass
