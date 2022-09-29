from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from onboarding_app import exceptions, models, schemas


def create_user(db: Session, stock: schemas.StockCreate) -> models.Stock:
    try:
        db_stock = models.Stock(code=stock.code, market=stock.market, name=stock.name)
        db.add(db_stock)
        db.commit()
        db.refresh(db_stock)
    except IntegrityError:
        raise exceptions.DuplicatedError
    return db_stock


def get_stocks(db: Session, offset: int = 0, limit: int = 100) -> list[models.Stock]:
    return db.query(models.Stock).offset(offset).limit(limit).all()


def get_stock(stock_id: int, db: Session) -> models.Stock:
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id)
    if not db_stock.first():
        raise exceptions.DataDoesNotExistError
    return db_stock.first()


def update_stock(
    stock_id: int, stock: schemas.StockCreate, db: Session
) -> models.Stock:
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id)
    if not db_stock.first():
        raise exceptions.DataDoesNotExistError

    db_stock.update(stock.dict(exclude_unset=True))
    db.commit()
    db.refresh(db_stock)
    return db_stock.first()


def delete_stock(stock_id: int, db: Session) -> models.Stock:
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id)
    if not db_stock.first():
        raise exceptions.DataDoesNotExistError
    db_stock.delete()
    db.commit()
    return db_stock
