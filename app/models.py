from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer,
    Numeric, String, Text, UniqueConstraint, extract, func, select,
)
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from app.database import Base

# BIGINT di PostgreSQL; INTEGER di SQLite (hanya agar autoincrement berjalan saat testing)
BigInt = BigInteger().with_variant(Integer, "sqlite")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('user', 'admin')", name="ck_users_role"),)

    id: Mapped[int] = mapped_column(BigInt, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(10), default="user", server_default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("name", "type", name="uq_categories_name_type"),
        CheckConstraint("type IN ('income', 'expense')", name="ck_categories_type"),
    )

    id: Mapped[int] = mapped_column(BigInt, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(10))


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(BigInt, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')", name="ck_transactions_type"),
        CheckConstraint("amount > 0", name="ck_transactions_amount"),
        Index("idx_transactions_user_date", "user_id", "transaction_date"),
        Index("idx_transactions_category", "category_id"),
    )

    id: Mapped[int] = mapped_column(BigInt, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInt, ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(BigInt, ForeignKey("categories.id", ondelete="RESTRICT"))
    payment_method_id: Mapped[int] = mapped_column(BigInt, ForeignKey("payment_methods.id", ondelete="RESTRICT"))
    type: Mapped[str] = mapped_column(String(10))
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    description: Mapped[str | None] = mapped_column(Text)
    transaction_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    category: Mapped[Category] = relationship(lazy="joined")
    payment_method: Mapped[PaymentMethod] = relationship(lazy="joined")

    @property
    def category_name(self) -> str:
        return self.category.name

    @property
    def payment_method_name(self) -> str:
        return self.payment_method.name


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", "month", "year", name="uq_budgets_user_category_period"),
        CheckConstraint("amount > 0", name="ck_budgets_amount"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_budgets_month"),
        CheckConstraint("year BETWEEN 2000 AND 2100", name="ck_budgets_year"),
    )

    id: Mapped[int] = mapped_column(BigInt, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInt, ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(BigInt, ForeignKey("categories.id", ondelete="RESTRICT"))
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    month: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)

    category: Mapped[Category] = relationship(lazy="joined")

    @property
    def category_name(self) -> str:
        return self.category.name


# "spent" = total pengeluaran kategori tsb pada bulan/tahun anggaran (dihitung di database)
Budget.__mapper__.add_property(
    "spent",
    column_property(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(
            Transaction.user_id == Budget.user_id,
            Transaction.category_id == Budget.category_id,
            Transaction.type == "expense",
            extract("month", Transaction.transaction_date) == Budget.month,
            extract("year", Transaction.transaction_date) == Budget.year,
        )
        .correlate_except(Transaction)
        .scalar_subquery()
    ),
)
