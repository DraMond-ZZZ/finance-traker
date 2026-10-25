import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DataError, IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("finance-tracker")

PG_MESSAGES = {
    "23505": "Data sudah ada (duplikat)",
    "23503": "Data masih dipakai oleh data lain atau referensi tidak valid",
    "23514": "Data melanggar aturan database",
}


def _error(message: str, status: int, headers: dict | None = None) -> JSONResponse:
    return JSONResponse({"error": message}, status_code=status, headers=headers)


def _format_validation(exc: RequestValidationError) -> str:
    parts = []
    for err in exc.errors():
        loc = err.get("loc", ())
        if loc and loc[0] == "path":
            return "ID tidak valid"
        if err.get("type") == "json_invalid":
            return "Format JSON tidak valid"
        field = ".".join(str(x) for x in loc[1:])
        msg = "wajib diisi" if err.get("type") == "missing" else err.get("msg", "tidak valid")
        parts.append(f"{field}: {msg}" if field else msg)
    return "; ".join(parts) or "Input tidak valid"


def register_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        detail = exc.detail
        if exc.status_code == 404 and detail == "Not Found":
            detail = "Endpoint tidak ditemukan"
        elif exc.status_code == 405:
            detail = "Method tidak diizinkan"
        return _error(str(detail), exc.status_code, getattr(exc, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return _error(_format_validation(exc), 400)

    @app.exception_handler(IntegrityError)
    async def integrity_error(request: Request, exc: IntegrityError):
        code = getattr(exc.orig, "sqlstate", None)
        message = PG_MESSAGES.get(code)
        if message is None:
            text = str(exc.orig).lower()
            if "unique" in text:
                message = PG_MESSAGES["23505"]
            elif "foreign key" in text:
                message = PG_MESSAGES["23503"]
            else:
                message = "Data melanggar aturan database"
        return _error(message, 400)

    @app.exception_handler(DataError)
    async def data_error(request: Request, exc: DataError):
        return _error("Format input tidak valid", 400)

    @app.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception):
        logger.exception("Unhandled error", exc_info=exc)
        return _error("Terjadi kesalahan pada server", 500)
