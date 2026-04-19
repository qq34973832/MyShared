from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.user import User, UserRole
from app.dependencies.auth import get_current_user
from typing import List


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求用户是管理员"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_merchant(current_user: User = Depends(get_current_user)) -> User:
    """要求用户是商家"""
    if current_user.role != UserRole.MERCHANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Merchant access required"
        )
    return current_user


def require_consumer(current_user: User = Depends(get_current_user)) -> User:
    """要求用户是消费者"""
    if current_user.role not in [UserRole.CONSUMER, UserRole.GUEST]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consumer access required"
        )
    return current_user


def require_permission(
    permission: str,
    current_user: User = Depends(get_current_user)
) -> User:
    """要求用户拥有特定权限"""
    if permission not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission}' required"
        )
    return current_user
