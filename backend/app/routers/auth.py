from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, Token
from ..auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if len(data.username.strip()) < 3 or len(data.password) < 4:
        raise HTTPException(400, "Логин минимум 3 символа, пароль минимум 4")
    if db.query(User).filter(User.username == data.username.strip()).first():
        raise HTTPException(400, "Такой пользователь уже существует")
    user = User(username=data.username.strip(), password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_token(user.id), "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(401, "Неверный логин или пароль")
    return {"access_token": create_token(user.id), "token_type": "bearer"}
