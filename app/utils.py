from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from pydantic import BaseModel

from app.models import User


def ok(message: str, data) -> dict:
    return {"message": message, "data": data}


def ok_list(message: str, rows) -> dict:
    return {"message": message, "count": len(rows), "data": rows}


def is_admin(user: User) -> bool:
    return user.role == "admin"


def today_wib() -> date:
    return datetime.now(ZoneInfo("Asia/Jakarta")).date()


def patch_data(body: BaseModel, nullable: tuple[str, ...] = ()) -> dict:
    """Ambil hanya field yang dikirim pada PATCH; tolak body kosong dan nilai null pada field wajib."""
    data = body.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="Tidak ada field yang diubah")
    nulls = [k for k, v in data.items() if v is None and k not in nullable]
    if nulls:
        raise HTTPException(status_code=400, detail=f"{', '.join(nulls)} tidak boleh null")
    return data
