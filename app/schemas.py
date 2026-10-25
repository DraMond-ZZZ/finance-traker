from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import (
    BaseModel, BeforeValidator, ConfigDict, EmailStr, Field, StringConstraints, field_validator,
)

T = TypeVar("T")

TxType = Literal["income", "expense"]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Password = Annotated[str, StringConstraints(min_length=6, max_length=72)]
Money = Annotated[Decimal, Field(gt=0, max_digits=15, decimal_places=2)]
Num = Annotated[float, BeforeValidator(lambda v: float(v) if isinstance(v, Decimal) else v)]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Envelope response ----------
class Msg(BaseModel):
    message: str


class One(BaseModel, Generic[T]):
    message: str
    data: T


class Many(BaseModel, Generic[T]):
    message: str
    count: int
    data: list[T]


# ---------- Users & Auth ----------
def _lower(v):
    return v.lower() if isinstance(v, str) else v


class UserCreate(BaseModel):
    name: Name
    email: EmailStr
    password: Password

    lower_email = field_validator("email")(_lower)


class UserReplace(BaseModel):
    name: Name
    email: EmailStr
    password: Password | None = None

    lower_email = field_validator("email")(_lower)


class UserPatch(BaseModel):
    name: Name | None = None
    email: EmailStr | None = None
    password: Password | None = None

    lower_email = field_validator("email")(_lower)


class LoginIn(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserOut(ORM):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime


class AuthOut(BaseModel):
    message: str
    data: UserOut
    token: str


# ---------- Categories ----------
class CategoryIn(BaseModel):
    name: Name
    type: TxType


class CategoryPatch(BaseModel):
    name: Name | None = None
    type: TxType | None = None


class CategoryOut(ORM):
    id: int
    name: str
    type: str


# ---------- Payment methods ----------
class PaymentMethodIn(BaseModel):
    name: Name


class PaymentMethodPatch(BaseModel):
    name: Name | None = None


class PaymentMethodOut(ORM):
    id: int
    name: str


# ---------- Transactions ----------
class TransactionBase(BaseModel):
    category_id: int = Field(gt=0)
    payment_method_id: int = Field(gt=0)
    type: TxType
    amount: Money
    description: str | None = Field(default=None, max_length=1000)
    transaction_date: date | None = Field(default=None, description="YYYY-MM-DD, default hari ini")


class TransactionCreate(TransactionBase):
    user_id: int | None = Field(default=None, gt=0, description="Diabaikan untuk user biasa; wajib untuk admin")


class TransactionPatch(BaseModel):
    user_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)
    payment_method_id: int | None = Field(default=None, gt=0)
    type: TxType | None = None
    amount: Money | None = None
    description: str | None = Field(default=None, max_length=1000)
    transaction_date: date | None = None


class TransactionOut(ORM):
    id: int
    user_id: int
    category_id: int
    category_name: str
    payment_method_id: int
    payment_method_name: str
    type: str
    amount: Num
    description: str | None
    transaction_date: date
    created_at: datetime


# ---------- Budgets ----------
class BudgetBase(BaseModel):
    category_id: int = Field(gt=0)
    amount: Money
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)


class BudgetCreate(BudgetBase):
    user_id: int | None = Field(default=None, gt=0, description="Diabaikan untuk user biasa; wajib untuk admin")


class BudgetPatch(BaseModel):
    user_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)
    amount: Money | None = None
    month: int | None = Field(default=None, ge=1, le=12)
    year: int | None = Field(default=None, ge=2000, le=2100)


class BudgetOut(ORM):
    id: int
    user_id: int
    category_id: int
    category_name: str
    amount: Num
    month: int
    year: int
    spent: Num
