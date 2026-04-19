from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.user import User
from app.models.comment import Comment
from app.models.shared_product import SharedProduct
from app.schemas.comment import (
    CommentCreate, CommentResponse, CommentUpdate
)
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("", response_model=CommentResponse)
def create_comment(
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建评论"""
    product = db.query(SharedProduct).filter(
        SharedProduct.id == comment_in.product_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    comment = Comment(
        user_id=current_user.id,
        product_id=product.id,
        merchant_id=product.merchant_id,
        rating=comment_in.rating,
        title=comment_in.title,
        content=comment_in.content,
        image_urls=comment_in.image_urls,
        is_verified_purchase=1
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment


@router.get("/product/{product_id}", response_model=list[CommentResponse])
def list_product_comments(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取商品的评论列表"""
    product = db.query(SharedProduct).filter(
        SharedProduct.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return db.query(Comment).filter(
        Comment.product_id == product_id
    ).offset(skip).limit(limit).all()


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """获取评论详情"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return comment


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新评论"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if comment_in.rating:
        comment.rating = comment_in.rating
    if comment_in.title:
        comment.title = comment_in.title
    if comment_in.content:
        comment.content = comment_in.content
    
    db.commit()
    db.refresh(comment)
    
    return comment


@router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除评论"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(comment)
    db.commit()
