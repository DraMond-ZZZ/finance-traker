from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.deps import DB, CurrentUser
from app.models import User
from app.schemas import AuthOut, LoginIn, One, UserCreate, UserOut
from app.security import DUMMY_HASH, create_token, hash_password, verify_password
from app.utils import ok

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", status_code=201, response_model=AuthOut, summary="Daftar akun baru")
def register(body: UserCreate, db: DB):
    # role selalu 'user' untuk registrasi publik
    user = User(name=body.name, email=body.email, password=hash_password(body.password), role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Registrasi berhasil", "data": user, "token": create_token(user.id)}


@router.post("/login", response_model=AuthOut, summary="Login dan dapatkan token JWT")
def login(body: LoginIn, db: DB):
    user = db.scalar(select(User).where(User.email == body.email.strip().lower()))
    valid = verify_password(body.password, user.password if user else DUMMY_HASH)
    if user is None or not valid:
        raise HTTPException(status_code=401, detail="Email atau password salah")
    return {"message": "Login berhasil", "data": user, "token": create_token(user.id)}


@router.get("/me", response_model=One[UserOut], summary="Profil user yang sedang login")
def me(user: CurrentUser):
    return ok("Profil berhasil diambil", user)
