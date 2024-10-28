from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import logging

from app.crud.user import get_user_by_username
from app.models.user import User
from app.schemas.token import TokenData
from app.core import security
from app.core.config import settings
from app.db.base import SessionLocal

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security_scheme = HTTPBearer()

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> User:
    try:
        token = credentials.credentials
        logger.info(f"Validating token...")
        
        # 验证token格式和有效性
        payload = security.verify_token(token)
        if not payload:
            logger.error("Token validation failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        if not username:
            logger.error("Token missing username claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证令牌缺少用户信息",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 获取用户
        user = get_user_by_username(db, username=username)
        if not user:
            logger.error(f"User not found: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 验证用户状态
        if not user.is_active:
            logger.error(f"Inactive user attempted access: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户账号未激活",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌格式",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        logger.error(f"Unexpected error in authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # 改为 401 而不是 500
            detail="认证过程中发生错误",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user