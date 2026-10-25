from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select

from app.deps import DB, CurrentUser, get_current_user
from app.models import Budget, Category, User
from app.schemas import BudgetCreate, BudgetOut, BudgetPatch, Many, Msg, One
from app.utils import is_admin, ok, ok_list, patch_data

router = APIRouter(prefix="/api/budgets", tags=["Budgets"], dependencies=[Depends(get_current_user)])
ID = Annotated[int, Path(gt=0)]


def _get_or_404(db, budget_id: int, current: User) -> Budget:
    budget = db.get(Budget, budget_id)
    if budget is None or (not is_admin(current) and budget.user_id != current.id):
        raise HTTPException(status_code=404, detail="Anggaran tidak ditemukan")
    return budget


def _ensure_refs(db, user_id: int, category_id: int) -> None:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    if db.get(Category, category_id) is None:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")


@router.get("", response_model=Many[BudgetOut], summary="Daftar anggaran (termasuk total pengeluaran 'spent')")
def list_budgets(db: DB, current: CurrentUser):
    query = select(Budget).order_by(Budget.id)
    if not is_admin(current):
        query = query.where(Budget.user_id == current.id)
    return ok_list("Data anggaran berhasil diambil", db.scalars(query).all())


@router.get("/{budget_id}", response_model=One[BudgetOut])
def get_budget(budget_id: ID, db: DB, current: CurrentUser):
    return ok("Anggaran berhasil diambil", _get_or_404(db, budget_id, current))


@router.post("", status_code=201, response_model=One[BudgetOut])
def create_budget(body: BudgetCreate, db: DB, current: CurrentUser):
    owner_id = body.user_id if is_admin(current) else current.id
    if owner_id is None:
        raise HTTPException(status_code=400, detail="user_id wajib diisi (khusus admin)")
    _ensure_refs(db, owner_id, body.category_id)
    budget = Budget(user_id=owner_id, **body.model_dump(exclude={"user_id"}))
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return ok("Anggaran berhasil ditambahkan", budget)


@router.put("/{budget_id}", response_model=One[BudgetOut])
def replace_budget(budget_id: ID, body: BudgetCreate, db: DB, current: CurrentUser):
    budget = _get_or_404(db, budget_id, current)
    owner_id = (body.user_id or budget.user_id) if is_admin(current) else current.id
    _ensure_refs(db, owner_id, body.category_id)
    for key, value in {**body.model_dump(exclude={"user_id"}), "user_id": owner_id}.items():
        setattr(budget, key, value)
    db.commit()
    db.refresh(budget)
    return ok("Anggaran berhasil diperbarui", budget)


@router.patch("/{budget_id}", response_model=One[BudgetOut])
def patch_budget(budget_id: ID, body: BudgetPatch, db: DB, current: CurrentUser):
    budget = _get_or_404(db, budget_id, current)
    data = patch_data(body)
    if not is_admin(current):
        data.pop("user_id", None)
    if not data:
        raise HTTPException(status_code=400, detail="Tidak ada field yang diubah")
    _ensure_refs(db, data.get("user_id", budget.user_id), data.get("category_id", budget.category_id))
    for key, value in data.items():
        setattr(budget, key, value)
    db.commit()
    db.refresh(budget)
    return ok("Anggaran berhasil diperbarui", budget)


@router.delete("/{budget_id}", response_model=Msg)
def delete_budget(budget_id: ID, db: DB, current: CurrentUser):
    budget = _get_or_404(db, budget_id, current)
    db.delete(budget)
    db.commit()
    return {"message": "Anggaran berhasil dihapus"}
