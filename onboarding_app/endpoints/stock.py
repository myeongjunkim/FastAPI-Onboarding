from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from onboarding_app import database, schemas
from onboarding_app.queries import stock as stock_query

stock_router = APIRouter()


@stock_router.post("/stocks", response_model=schemas.Stock)
def create_stock(stock: schemas.StockCreate, db: Session = Depends(database.get_db)):
    return stock_query.create_user(db=db, stock=stock)


@stock_router.get("/stocks", response_model=list[schemas.Stock])
def fetch_stocks(db: Session = Depends(database.get_db)):
    return stock_query.get_stocks(db=db)


@stock_router.get("/stocks/{stock_id}", response_model=schemas.Stock)
def get_stock(stock_id: int, db: Session = Depends(database.get_db)):
    return stock_query.get_stock(db=db, stock_id=stock_id)


@stock_router.delete("/stocks/{stock_id}")
def delete_stock(stock_id: int, db: Session = Depends(database.get_db)):
    stock_query.delete_stock(stock_id=stock_id, db=db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Stock deleted successfully"},
    )


@stock_router.put("/stocks/{stock_id}", response_model=schemas.Stock)
def update_stock(
    stock: schemas.StockCreate, stock_id: int, db: Session = Depends(database.get_db)
):
    return stock_query.update_stock(db=db, stock=stock, stock_id=stock_id)
