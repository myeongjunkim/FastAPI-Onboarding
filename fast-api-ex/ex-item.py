from typing import Union

from fastapi import Body, Cookie, FastAPI, Header, Path, Query, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, HttpUrl

app = FastAPI()


# fake_db
items = {
    "foo": {"name": "Foo", "description": "The foo", "price": 12, "tax": 5.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5},
}


# 자료 구조 설정
class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    user_agent: Union[str, None] = Header(default=None)
    name: str
    description: Union[str, None] = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(
        default=None, ge=0, description="The price must be greater than zero"
    )
    tax: Union[float, None] = None
    tags: list[str] = []
    image: Union[Image, None] = None


class User(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Union[str, None] = None


@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"main": "root"}


@app.get("/items/", status_code=status.HTTP_200_OK)
async def read_items(
    q: Union[str, None] = Query(default=None, max_length=50),
    ads_id: Union[str, None] = Cookie(default=None),
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}], "ads_id": ads_id}

    if q:
        results.update({"q": [{"q": q}, {"q2": q}]})
    return results


@app.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item


@app.get("/items/{item_id}", status_code=status.HTTP_200_OK)
async def read_item(
    item_id: int = Path(title="The ID of the item to get"),
    q: Union[str, None] = Query(default=None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": jsonable_encoder(q)})
    return results


@app.put("/items/{item_id}", status_code=status.HTTP_202_ACCEPTED)
async def put_item(
    *,
    item_id: int,
    item: Item,
    user: User,
    importance: int = Body(ge=0),
    q: Union[str, None] = None
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results


@app.patch("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    # stored_item_data = items[item_id] # type: none
    stored_item_data = {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5}
    stored_item_model = Item(**stored_item_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item
