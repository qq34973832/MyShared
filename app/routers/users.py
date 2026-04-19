from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate, UserResponse, LoginRequest, TokenResponse,
    UserUpdate, UserBanRequest, UserDetailResponse
)
from app.dependencies.auth import get_current_user
from app.dependencies.role import require_admin
from datetime import timedelta

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户是否已存在
    existing_user = db.query(User).filter(
        (User.email == user_in.email) | (User.username == user_in.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # 创建新用户
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=UserRole.CONSUMER,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User is banned: {user.ban_reason}"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    # 创建令牌
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 1800
    }


@router.get("/me", response_model=UserDetailResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    if user_in.username:
        existing = db.query(User).filter(
            User.username == user_in.username,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = user_in.username
    
    if user_in.email:
        existing = db.query(User).filter(
            User.email == user_in.email,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_in.email
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=204)
def delete_current_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除当前用户账户"""
    db.delete(current_user)
    db.commit()


@router.post("/{user_id}/ban", response_model=UserResponse)
def ban_user(
    user_id: int,
    ban_request: UserBanRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """封禁用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_banned = ban_request.is_banned
    user.ban_reason = ban_request.ban_reason
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=list[UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表（仅管理员）"""
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取用户详情（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
