from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, UserOut
from auth_deps import get_current_user
import auth_utils

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(data: UserCreate, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    existing = db.scalar(select(User).where(func.lower(User.email) == email))
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    user = User(
        email=email,
        nombre=data.nombre,
        hashed_password=auth_utils.hash_password(data.password),
        nivel="A1",
        is_premium=False,
        plan="free",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    try:
        from mail import send_welcome
        send_welcome(user.email, user.nombre)
    except Exception as e:
        print(f"AVISO: no se envió correo de bienvenida: {e}")
    return user


@router.post("/login", response_model=dict)
def login(data: UserLogin, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    if not user or not auth_utils.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = auth_utils.create_token(user.id)
    return {"token": token, "user": UserOut.model_validate(user)}


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current
