from typing import Optional

from pydantic import BaseModel, constr, EmailStr, validator


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    hashed_password = str
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: constr(min_length=4, max_length=20)  # type:ignore
    email: EmailStr
    password1: constr(min_length=4, max_length=20)  # type:ignore
    password2: str

    @validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        if "password1" in values and v != values["password1"]:
            raise ValueError("passwords do not match")
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class Stock(BaseModel):
    id: int
    code: str
    market: str
    name: str
    price: int


class StockCreate(BaseModel):
    code: str
    market: str
    name: str
    price: int


class Wishlist(BaseModel):
    id: int
    user_id: int
    name: str
    description: str
    created_at: str
    updated_at: str
    is_open: bool
    order_num: int

    class Config:
        orm_mode = True


class WishlistCreate(BaseModel):
    name: str
    description: str


class WishlistUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


class WishStock(BaseModel):
    id: int
    wishlist_id: int
    stock_id: int
    purchase_price: int
    holding_num: int
    order_num: int

    class Config:
        orm_mode = True


class WishStockCreate(BaseModel):
    stock_id: int
    purchase_price: int
    holding_num: int


class WishStockUpdate(BaseModel):
    purchase_price: Optional[int]
    holding_num: Optional[int]


class WishStockResponse(BaseModel):
    stock: Stock
    order_num: int
    purchase_price: int
    holding_num: int
    return_rate: float


class History(BaseModel):
    body: str
    created_at: str

    class Config:
        orm_mode = True


class Comment(BaseModel):
    id: int
    user_id: int
    wishlist_id: int
    body: str
    is_reply: bool
    parent_id: Optional[int]

    class Config:
        orm_mode = True


class CommentCreate(BaseModel):
    body: str
