from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError
import logging
from app.api import deps
from app.crud.user import get_user_by_email, get_user_by_username, create_user
from app.schemas import user as user_schemas
from app.db.base import get_db
from app.models.user import User  # 更新导入，直接从 user.py 导入 User 模型

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=user_schemas.UserResponse)
def create_user_endpoint(
    user: user_schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    try:
        # 检查邮箱是否已注册
        if get_user_by_email(db, email=user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 检查用户名是否已注册
        if get_user_by_username(db, username=user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # 创建用户
        db_user = create_user(db=db, user=user)
        
        # 转换为响应模型
        return user_schemas.UserResponse(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.full_name,
            is_active=db_user.is_active
        )
        
    except HTTPException as he:
        # 重新抛出 HTTP 异常
        raise he
    except IntegrityError:
        # 处理数据库唯一性约束错误
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    except Exception as e:
        # 记录错误日志（在实际生产环境中应该使用proper logging）
        print(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating user: {str(e)}"
        )

@router.get("/", response_model=List[user_schemas.UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        # 更新这里，使用导入的 User 模型
        users = db.query(User).offset(skip).limit(limit).all()
        return [
            user_schemas.UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/me", response_model=user_schemas.UserResponse)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    获取当前登录用户信息
    """
    try:
        # 显式创建响应对象
        return {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "full_name": current_user.full_name or "",  # 处理可能为 None 的情况
            "is_active": current_user.is_active
        }
    except Exception as e:
        logger.error(f"Error in read_user_me: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving user information: {str(e)}"
        )