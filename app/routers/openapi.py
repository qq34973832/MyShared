from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.user import User
from app.models.api_token import APIToken
from app.schemas.openapi import (
    APITokenCreate, APITokenResponse, APITokenListResponse,
    APITokenRevokeRequest
)
from app.dependencies.auth import get_current_user
from app.utils.helpers import generate_api_token, mask_token, is_token_expired
from datetime import datetime, timezone

router = APIRouter(prefix="/openapi", tags=["openapi"])


@router.post("/tokens", response_model=APITokenResponse)
def create_api_token(
    token_in: APITokenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建 API Token"""
    token = generate_api_token()
    
    api_token = APIToken(
        user_id=current_user.id,
        token=token,
        name=token_in.name,
        scopes=token_in.scopes,
        expires_at=token_in.expires_at,
        allowed_ips=token_in.allowed_ips or []
    )
    
    db.add(api_token)
    db.commit()
    db.refresh(api_token)
    
    return api_token


@router.get("/tokens", response_model=list[APITokenListResponse])
def list_api_tokens(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取 API Token 列表"""
    tokens = db.query(APIToken).filter(
        APIToken.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [
        {
            **token.__dict__,
            "token": mask_token(token.token)  # 隐藏完整 Token
        } for token in tokens
    ]


@router.delete("/tokens/{token_id}", status_code=204)
def revoke_api_token(
    token_id: int,
    revoke_in: APITokenRevokeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """撤销 API Token"""
    api_token = db.query(APIToken).filter(
        APIToken.id == token_id,
        APIToken.user_id == current_user.id
    ).first()
    
    if not api_token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    api_token.is_revoked = True
    db.commit()


@router.post("/tokens/{token_id}/refresh", response_model=APITokenResponse)
def refresh_api_token(
    token_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """刷新 API Token"""
    api_token = db.query(APIToken).filter(
        APIToken.id == token_id,
        APIToken.user_id == current_user.id
    ).first()
    
    if not api_token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    # 生成新 Token
    new_token = generate_api_token()
    api_token.token = new_token
    api_token.created_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(api_token)
    
    return api_token


@router.get("/tokens/{token_id}/check", response_model=dict)
def check_api_token(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """检查 API Token 的有效性和权限"""
    api_token = db.query(APIToken).filter(APIToken.token == token).first()
    
    if not api_token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    if api_token.is_revoked:
        raise HTTPException(status_code=403, detail="Token is revoked")
    
    if not api_token.is_active:
        raise HTTPException(status_code=403, detail="Token is inactive")
    
    if is_token_expired(api_token.expires_at):
        raise HTTPException(status_code=403, detail="Token is expired")
    
    # 更新最后使用时间
    api_token.last_used_at = datetime.now(timezone.utc)
    db.commit()
    
    return {
        "valid": True,
        "scopes": api_token.scopes,
        "user_id": api_token.user_id,
        "expires_at": api_token.expires_at
    }
