import typing as t
from pydantic import BaseModel, Field
from typing import List, Any, Optional
from fastapi import Request


class TableTemplateContext(BaseModel):
    request: Request
    table_name: str
    columns: List[str]
    data: List[Any]
    page: int = Field(ge=1)
    per_page: int = Field(ge=1, le=100)
    total_pages: int = Field(ge=1)
    total_items: int = Field(ge=0)
    sort_by: Optional[str] = None
    sort_order: str = Field(pattern="^(asc|desc)$")

    class Config:
        arbitrary_types_allowed = True


class Name(BaseModel):
    firstname: str
    lastname: str


class Geolocation(BaseModel):
    lat: float
    long: float


class Address(BaseModel):
    city: str
    street: str
    number: str
    zipcode: str
    geolocation: Geolocation


class User(BaseModel):
    id: int
    email: str
    username: str
    password: str
    name: Name
    address: Address
    phone: str


class UsersResponse(BaseModel):
    status: str
    message: str
    users: t.List[User]


class Product(BaseModel):
    id: int
    title: str
    image: str
    price: float
    description: str
    brand: str
    model: str
    color: t.Optional[str] = None
    category: str
    discount: t.Optional[int] = None
    popular: t.Optional[bool] = None
    onSale: t.Optional[bool] = None


class ProductsResponse(BaseModel):
    status: str
    message: str
    products: t.List[Product]
