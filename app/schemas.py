from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Message(APIModel):
    message: str


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(APIModel):
    id: int
    name: str
    email: EmailStr
    role: str


class SessionOut(BaseModel):
    user: UserOut
    csrf_token: str


class CategoryOut(APIModel):
    id: int
    name: str
    slug: str


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    slug: str = Field(pattern=r"^[a-z0-9-]+$", max_length=100)


class VariantOut(APIModel):
    id: int
    size: str
    stock: int


class ProductOut(APIModel):
    id: int
    category: CategoryOut
    name: str
    slug: str
    description: str
    price_cents: int
    image_url: str | None
    is_active: bool
    variants: list[VariantOut]


class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=2, max_length=160)
    slug: str = Field(pattern=r"^[a-z0-9-]+$", max_length=180)
    description: str = Field(min_length=5)
    price_cents: int = Field(gt=0)
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool = True


class ProductUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=2, max_length=160)
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9-]+$", max_length=180)
    description: str | None = Field(default=None, min_length=5)
    price_cents: int | None = Field(default=None, gt=0)
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class VariantCreate(BaseModel):
    size: str = Field(min_length=1, max_length=20)
    stock: int = Field(ge=0)


class CartItemCreate(BaseModel):
    variant_id: int
    quantity: int = Field(ge=1, le=10)


class CartItemOut(APIModel):
    id: int
    quantity: int
    variant: VariantOut
    product: ProductOut


class CartOut(BaseModel):
    items: list[CartItemOut]
    total_cents: int


class OrderItemOut(APIModel):
    product_name: str
    size: str
    unit_price_cents: int
    quantity: int


class OrderOut(APIModel):
    id: int
    total_cents: int
    status: str
    payment_status: str
    created_at: datetime
    items: list[OrderItemOut]


class CheckoutOut(BaseModel):
    order: OrderOut
    checkout_url: str


class OrderStatusUpdate(BaseModel):
    status: Literal["available", "picked_up"]
