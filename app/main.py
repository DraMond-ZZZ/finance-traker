from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.errors import register_handlers
from app.routers import auth, budgets, categories, payment_methods, transactions, users

app = FastAPI(
    title="Web Pencatatan Keuangan - REST API",
    version="1.0.0",
    description=(
        "REST API untuk mencatat pemasukan dan pengeluaran. "
        "Daftar/login lewat `/api/auth/*`, lalu klik **Authorize** dan tempel token JWT."
    ),
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
register_handlers(app)


WEB = Path(__file__).parent / "web"
app.mount("/static", StaticFiles(directory=WEB / "static"), name="static")


@app.get("/", include_in_schema=False)
def landing():
    return FileResponse(WEB / "index.html")


@app.get("/login", include_in_schema=False)
def login_page():
    return FileResponse(WEB / "login.html")


@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return FileResponse(WEB / "dashboard.html")


@app.get("/api", include_in_schema=False)
def api_info():
    return {
        "message": "Web Pencatatan Keuangan - REST API",
        "docs": "/docs",
        "auth": ["POST /api/auth/register", "POST /api/auth/login", "GET /api/auth/me"],
        "endpoints": ["/api/users", "/api/categories", "/api/payment-methods", "/api/transactions", "/api/budgets"],
    }


# Registrasi & login publik; semua router lain mewajibkan token (dependency di tiap router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(payment_methods.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
