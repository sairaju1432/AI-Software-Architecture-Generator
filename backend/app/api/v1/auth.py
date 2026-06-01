import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import Subscription, User
from app.schemas.dto import GoogleLoginRequest, LoginRequest, Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), full_name=payload.full_name)
    db.add(user)
    db.flush()
    db.add(Subscription(user_id=user.id))
    db.commit()
    db.refresh(user)
    return Token(access_token=create_access_token(user.id))


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=create_access_token(user.id))


@router.post("/google", response_model=Token)
async def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": payload.id_token})
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google ID token")
    profile = response.json()
    if settings.google_client_id and profile.get("aud") != settings.google_client_id:
        raise HTTPException(status_code=401, detail="Google token audience mismatch")
    email = profile.get("email")
    google_sub = profile.get("sub")
    if not email or not google_sub:
        raise HTTPException(status_code=401, detail="Google token is missing identity claims")

    user = db.query(User).filter((User.google_sub == google_sub) | (User.email == email)).first()
    if not user:
        user = User(email=email, google_sub=google_sub, full_name=profile.get("name", ""), hashed_password=None)
        db.add(user)
        db.flush()
        db.add(Subscription(user_id=user.id))
    else:
        user.google_sub = user.google_sub or google_sub
    db.commit()
    db.refresh(user)
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(current_user)):
    return user
