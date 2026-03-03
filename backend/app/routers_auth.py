from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import schemas
from .database import Base, engine
from .deps import get_db
from .models import User
from .security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或密码错误",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


def init_default_admins(db: Session) -> None:
    # 超级管理员：用于兜底管理，不允许在系统内被禁用或降级
    superadmin = db.query(User).filter(User.role == "superadmin").first()
    if not superadmin:
        root = User(
            username="superadmin",
            hashed_password=get_password_hash("superadmin123"),
            role="superadmin",
            is_active=True,
        )
        db.add(root)
        db.commit()

    # 普通管理员：方便日常使用，可以被其它管理员调整角色
    admin = db.query(User).filter(User.role == "admin").first()
    if not admin:
        default_username = "admin"
        default_password = "admin123"
        user = User(
            username=default_username,
            hashed_password=get_password_hash(default_password),
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.commit()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    try:
        init_default_admins(db)
    finally:
        db.close()

