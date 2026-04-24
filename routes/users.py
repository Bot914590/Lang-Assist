"""
Маршруты для работы с пользователями.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from models.models import Account
from schemas.user import UserCreate, UserResponse, UserLogin, UserUpdate
from utils.jwt import create_access_token, verify_token

router = APIRouter()


@router.post("/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Регистрация нового пользователя.
    """
    # Проверка существования email
    existing_email = db.query(Account).filter(Account.email == user_in.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Проверка существования username
    existing_username = db.query(Account).filter(Account.username == user_in.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Создание пользователя
    user = Account(
        email=user_in.email,
        username=user_in.username,
        lang_level=user_in.lang_level if hasattr(user_in, 'lang_level') else None,
    )
    user.set_password(user_in.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    # Создаем токен для нового пользователя
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=1440)
    )
    
    user_dict = UserResponse.model_validate(user).model_dump()
    user_dict["token"] = access_token
    return user_dict


@router.post("/users/login", response_model=UserResponse)
def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Авторизация пользователя.
    """
    user = db.query(Account).filter(Account.email == credentials.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.check_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Создаем токен с user_id
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=1440)
    )
    
    # Возвращаем пользователя с токеном (добавляем токен в response)
    user_dict = UserResponse.model_validate(user).model_dump()
    user_dict["token"] = access_token
    return user_dict


@router.get("/users/me", response_model=UserResponse)
def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Получить текущего пользователя.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = int(payload.get("sub"))
    user = db.query(Account).filter(Account.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Обновить профиль пользователя.
    """
    user = db.query(Account).filter(Account.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "password" and value:
            user.set_password(value)
        elif hasattr(user, field):
            setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Получить пользователя по ID.
    """
    user = db.query(Account).filter(Account.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
