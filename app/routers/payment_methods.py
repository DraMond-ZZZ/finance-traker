from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select

from app.deps import DB, get_current_user, require_admin
from app.models import PaymentMethod
from app.schemas import Many, Msg, One, PaymentMethodIn, PaymentMethodOut, PaymentMethodPatch
from app.utils import ok, ok_list, patch_data

router = APIRouter(prefix="/api/payment-methods", tags=["Payment Methods"], dependencies=[Depends(get_current_user)])
ID = Annotated[int, Path(gt=0)]
ADMIN = [Depends(require_admin)]  # tulis/ubah/hapus data bersama hanya untuk admin


def _get_or_404(db, method_id: int) -> PaymentMethod:
    method = db.get(PaymentMethod, method_id)
    if method is None:
        raise HTTPException(status_code=404, detail="Metode pembayaran tidak ditemukan")
    return method


@router.get("", response_model=Many[PaymentMethodOut])
def list_payment_methods(db: DB):
    rows = db.scalars(select(PaymentMethod).order_by(PaymentMethod.id)).all()
    return ok_list("Data metode pembayaran berhasil diambil", rows)


@router.get("/{method_id}", response_model=One[PaymentMethodOut])
def get_payment_method(method_id: ID, db: DB):
    return ok("Metode pembayaran berhasil diambil", _get_or_404(db, method_id))


@router.post("", status_code=201, response_model=One[PaymentMethodOut], dependencies=ADMIN, summary="Tambah metode pembayaran (admin)")
def create_payment_method(body: PaymentMethodIn, db: DB):
    method = PaymentMethod(**body.model_dump())
    db.add(method)
    db.commit()
    db.refresh(method)
    return ok("Metode pembayaran berhasil ditambahkan", method)


@router.put("/{method_id}", response_model=One[PaymentMethodOut], dependencies=ADMIN, summary="Ubah metode pembayaran (admin)")
def replace_payment_method(method_id: ID, body: PaymentMethodIn, db: DB):
    method = _get_or_404(db, method_id)
    method.name = body.name
    db.commit()
    db.refresh(method)
    return ok("Metode pembayaran berhasil diperbarui", method)


@router.patch("/{method_id}", response_model=One[PaymentMethodOut], dependencies=ADMIN, summary="Ubah sebagian metode pembayaran (admin)")
def patch_payment_method(method_id: ID, body: PaymentMethodPatch, db: DB):
    method = _get_or_404(db, method_id)
    for key, value in patch_data(body).items():
        setattr(method, key, value)
    db.commit()
    db.refresh(method)
    return ok("Metode pembayaran berhasil diperbarui", method)


@router.delete("/{method_id}", response_model=Msg, dependencies=ADMIN, summary="Hapus metode pembayaran (admin)")
def delete_payment_method(method_id: ID, db: DB):
    method = _get_or_404(db, method_id)
    db.delete(method)
    db.commit()
    return {"message": "Metode pembayaran berhasil dihapus"}
