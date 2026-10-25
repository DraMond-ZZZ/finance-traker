from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select

from app.deps import DB, AdminUser, CurrentUser, get_current_user
from app.models import User
from app.schemas import Many, Msg, One, UserCreate, UserOut, UserPatch, UserReplace
from app.security import hash_password
from app.utils import is_admin, ok, ok_list, patch_data

router = APIRouter(prefix="/api/users", tags=["Users"], dependencies=[Depends(get_current_user)])
ID = Annotated[int, Path(gt=0)]


def _get_or_404(db, user_id: int, current: User) -> User:
    # user biasa hanya boleh mengakses dirinya sendiri; selain itu dijawab 404 agar tidak membocorkan data
    user = db.get(User, user_id)
    if user is None or (not is_admin(current) and user.id != current.id):
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return user


@router.get("", response_model=Many[UserOut], summary="Daftar user (user biasa hanya melihat dirinya)")
def list_users(db: DB, current: CurrentUser):
    rows = db.scalars(select(User).order_by(User.id)).all() if is_admin(current) else [current]
    return ok_list("Data user berhasil diambil", rows)


@router.get("/{user_id}", response_model=One[UserOut])
def get_user(user_id: ID, db: DB, current: CurrentUser):
    return ok("User berhasil diambil", _get_or_404(db, user_id, current))


@router.post("", status_code=201, response_model=One[UserOut], summary="Tambah user (khusus admin)")
def create_user(body: UserCreate, db: DB, admin: AdminUser):
    user = User(name=body.name, email=body.email, password=hash_password(body.password), role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return ok("User berhasil ditambahkan", user)


@router.put("/{user_id}", response_model=One[UserOut])
def replace_user(user_id: ID, body: UserReplace, db: DB, current: CurrentUser):
    user = _get_or_404(db, user_id, current)
    user.name, user.email = body.name, body.email
    if body.password:
        user.password = hash_password(body.password)
    db.commit()
    db.refresh(user)
    return ok("User berhasil diperbarui", user)


@router.patch("/{user_id}", response_model=One[UserOut])
def patch_user(user_id: ID, body: UserPatch, db: DB, current: CurrentUser):
    user = _get_or_404(db, user_id, current)
    for key, value in patch_data(body).items():
        setattr(user, key, hash_password(value) if key == "password" else value)
    db.commit()
    db.refresh(user)
    return ok("User berhasil diperbarui", user)


@router.delete("/{user_id}", response_model=Msg)
def delete_user(user_id: ID, db: DB, current: CurrentUser):
    user = _get_or_404(db, user_id, current)
    db.delete(user)
    db.commit()
    return {"message": "User berhasil dihapus"}
