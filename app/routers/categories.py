from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select

from app.deps import DB, get_current_user, require_admin
from app.models import Category
from app.schemas import CategoryIn, CategoryOut, CategoryPatch, Many, Msg, One
from app.utils import ok, ok_list, patch_data

router = APIRouter(prefix="/api/categories", tags=["Categories"], dependencies=[Depends(get_current_user)])
ID = Annotated[int, Path(gt=0)]
ADMIN = [Depends(require_admin)]  # tulis/ubah/hapus data bersama hanya untuk admin


def _get_or_404(db, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    return category


@router.get("", response_model=Many[CategoryOut])
def list_categories(db: DB):
    return ok_list("Data kategori berhasil diambil", db.scalars(select(Category).order_by(Category.id)).all())


@router.get("/{category_id}", response_model=One[CategoryOut])
def get_category(category_id: ID, db: DB):
    return ok("Kategori berhasil diambil", _get_or_404(db, category_id))


@router.post("", status_code=201, response_model=One[CategoryOut], dependencies=ADMIN, summary="Tambah kategori (admin)")
def create_category(body: CategoryIn, db: DB):
    category = Category(**body.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return ok("Kategori berhasil ditambahkan", category)


@router.put("/{category_id}", response_model=One[CategoryOut], dependencies=ADMIN, summary="Ubah kategori (admin)")
def replace_category(category_id: ID, body: CategoryIn, db: DB):
    category = _get_or_404(db, category_id)
    for key, value in body.model_dump().items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return ok("Kategori berhasil diperbarui", category)


@router.patch("/{category_id}", response_model=One[CategoryOut], dependencies=ADMIN, summary="Ubah sebagian kategori (admin)")
def patch_category(category_id: ID, body: CategoryPatch, db: DB):
    category = _get_or_404(db, category_id)
    for key, value in patch_data(body).items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return ok("Kategori berhasil diperbarui", category)


@router.delete("/{category_id}", response_model=Msg, dependencies=ADMIN, summary="Hapus kategori (admin)")
def delete_category(category_id: ID, db: DB):
    category = _get_or_404(db, category_id)
    db.delete(category)
    db.commit()
    return {"message": "Kategori berhasil dihapus"}
