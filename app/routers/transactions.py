from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select

from app.deps import DB, CurrentUser, get_current_user
from app.models import Category, PaymentMethod, Transaction, User
from app.schemas import Many, Msg, One, TransactionCreate, TransactionOut, TransactionPatch, TxType
from app.utils import is_admin, ok, ok_list, patch_data, today_wib

router = APIRouter(prefix="/api/transactions", tags=["Transactions"], dependencies=[Depends(get_current_user)])
ID = Annotated[int, Path(gt=0)]


def _get_or_404(db, transaction_id: int, current: User) -> Transaction:
    # transaksi milik user lain dijawab 404 agar keberadaannya tidak bocor
    trx = db.get(Transaction, transaction_id)
    if trx is None or (not is_admin(current) and trx.user_id != current.id):
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    return trx


def _ensure_refs(db, user_id: int, category_id: int, payment_method_id: int) -> None:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    if db.get(Category, category_id) is None:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    if db.get(PaymentMethod, payment_method_id) is None:
        raise HTTPException(status_code=404, detail="Metode pembayaran tidak ditemukan")


@router.get("", response_model=Many[TransactionOut], summary="Daftar transaksi (dengan filter opsional)")
def list_transactions(
    db: DB,
    current: CurrentUser,
    user_id: int | None = None,
    category_id: int | None = None,
    payment_method_id: int | None = None,
    type_: Annotated[TxType | None, Query(alias="type")] = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    query = select(Transaction).order_by(Transaction.id)
    if not is_admin(current):
        query = query.where(Transaction.user_id == current.id)  # user biasa: hanya miliknya
    elif user_id is not None:
        query = query.where(Transaction.user_id == user_id)
    if category_id is not None:
        query = query.where(Transaction.category_id == category_id)
    if payment_method_id is not None:
        query = query.where(Transaction.payment_method_id == payment_method_id)
    if type_ is not None:
        query = query.where(Transaction.type == type_)
    if start_date is not None:
        query = query.where(Transaction.transaction_date >= start_date)
    if end_date is not None:
        query = query.where(Transaction.transaction_date <= end_date)
    return ok_list("Data transaksi berhasil diambil", db.scalars(query).all())


@router.get("/{transaction_id}", response_model=One[TransactionOut])
def get_transaction(transaction_id: ID, db: DB, current: CurrentUser):
    return ok("Transaksi berhasil diambil", _get_or_404(db, transaction_id, current))


@router.post("", status_code=201, response_model=One[TransactionOut])
def create_transaction(body: TransactionCreate, db: DB, current: CurrentUser):
    owner_id = body.user_id if is_admin(current) else current.id
    if owner_id is None:
        raise HTTPException(status_code=400, detail="user_id wajib diisi (khusus admin)")
    _ensure_refs(db, owner_id, body.category_id, body.payment_method_id)

    data = body.model_dump(exclude={"user_id"})
    data["transaction_date"] = data["transaction_date"] or today_wib()
    trx = Transaction(user_id=owner_id, **data)
    db.add(trx)
    db.commit()
    db.refresh(trx)
    return ok("Transaksi berhasil ditambahkan", trx)


@router.put("/{transaction_id}", response_model=One[TransactionOut])
def replace_transaction(transaction_id: ID, body: TransactionCreate, db: DB, current: CurrentUser):
    trx = _get_or_404(db, transaction_id, current)
    owner_id = (body.user_id or trx.user_id) if is_admin(current) else current.id
    _ensure_refs(db, owner_id, body.category_id, body.payment_method_id)

    data = body.model_dump(exclude={"user_id"})
    data["transaction_date"] = data["transaction_date"] or trx.transaction_date
    for key, value in {**data, "user_id": owner_id}.items():
        setattr(trx, key, value)
    db.commit()
    db.refresh(trx)
    return ok("Transaksi berhasil diperbarui", trx)


@router.patch("/{transaction_id}", response_model=One[TransactionOut])
def patch_transaction(transaction_id: ID, body: TransactionPatch, db: DB, current: CurrentUser):
    trx = _get_or_404(db, transaction_id, current)
    data = patch_data(body, nullable=("description",))
    if not is_admin(current):
        data.pop("user_id", None)  # user biasa tidak boleh memindahkan transaksi ke user lain
    if not data:
        raise HTTPException(status_code=400, detail="Tidak ada field yang diubah")
    _ensure_refs(
        db,
        data.get("user_id", trx.user_id),
        data.get("category_id", trx.category_id),
        data.get("payment_method_id", trx.payment_method_id),
    )
    for key, value in data.items():
        setattr(trx, key, value)
    db.commit()
    db.refresh(trx)
    return ok("Transaksi berhasil diperbarui", trx)


@router.delete("/{transaction_id}", response_model=Msg)
def delete_transaction(transaction_id: ID, db: DB, current: CurrentUser):
    trx = _get_or_404(db, transaction_id, current)
    db.delete(trx)
    db.commit()
    return {"message": "Transaksi berhasil dihapus"}
