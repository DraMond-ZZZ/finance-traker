"""Membuat tabel dan (opsional) data awal.

Pemakaian:
    python scripts/init_db.py            # buat tabel
    python scripts/init_db.py --seed     # buat tabel + data awal
    python scripts/init_db.py --reset --seed   # hapus semua tabel lalu buat ulang
"""
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app import models  # noqa: E402,F401
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Budget, Category, PaymentMethod, Transaction, User  # noqa: E402
from app.security import hash_password  # noqa: E402

CATEGORIES = [
    ("Gaji", "income"), ("Bonus", "income"), ("Lainnya", "income"),
    ("Makanan", "expense"), ("Transportasi", "expense"), ("Belanja", "expense"),
    ("Hiburan", "expense"), ("Lainnya", "expense"),
]
PAYMENT_METHODS = ["Cash", "Bank", "E-Wallet", "QRIS"]


def seed() -> None:
    with SessionLocal() as db:
        for name, type_ in CATEGORIES:
            if not db.scalar(select(Category).where(Category.name == name, Category.type == type_)):
                db.add(Category(name=name, type=type_))
        for name in PAYMENT_METHODS:
            if not db.scalar(select(PaymentMethod).where(PaymentMethod.name == name)):
                db.add(PaymentMethod(name=name))
        db.commit()

        if not db.scalar(select(User).where(User.email == "admin@example.com")):
            admin_password = os.getenv("ADMIN_PASSWORD") or "admin123"
            db.add(User(name="Administrator", email="admin@example.com",
                        password=hash_password(admin_password), role="admin"))

        if not db.scalar(select(User).where(User.email == "demo@example.com")):
            demo = User(name="Demo User", email="demo@example.com", password=hash_password("demo123"), role="user")
            db.add(demo)
            db.commit()

            def cat(name, type_):
                return db.scalar(select(Category).where(Category.name == name, Category.type == type_))

            def pay(name):
                return db.scalar(select(PaymentMethod).where(PaymentMethod.name == name))

            samples = [
                ("Gaji", "income", "Bank", 5_000_000, "Gaji bulanan", date(2026, 10, 1)),
                ("Makanan", "expense", "Cash", 25_000, "Makan siang", date(2026, 10, 19)),
                ("Transportasi", "expense", "E-Wallet", 15_000, "Ojek online", date(2026, 10, 19)),
            ]
            for category, type_, method, amount, description, when in samples:
                db.add(Transaction(user_id=demo.id, category_id=cat(category, type_).id,
                                   payment_method_id=pay(method).id, type=type_, amount=amount,
                                   description=description, transaction_date=when))
            db.add(Budget(user_id=demo.id, category_id=cat("Makanan", "expense").id,
                          amount=1_500_000, month=10, year=2026))
        db.commit()


def main() -> None:
    args = sys.argv[1:]
    if "--reset" in args:
        Base.metadata.drop_all(engine)
        print("Tabel lama dihapus")
    Base.metadata.create_all(engine)
    print("Tabel berhasil dibuat")
    if "--seed" in args:
        seed()
        print("Data awal berhasil dimasukkan")
        print("Akun: admin@example.com (admin) dan demo@example.com / demo123 (user biasa)")
        print("Untuk production, set ADMIN_PASSWORD sebelum seed dan ganti password akun demo.")


if __name__ == "__main__":
    main()
