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


class WishList(BaseModel):
    id: int
    user_id: int
    name: str
    description: str
    created_date: str
    updated_date: str
    is_open: bool
    order_method: int

    class Config:
        orm_mode = True


class StockCreate(BaseModel):
    code: str
    market: str
    name: str
    price: int


class WishListCreate(BaseModel):
    name: str
    description: str
