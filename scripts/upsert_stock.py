import csv

from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine.base import Engine

from onboarding_app import database, exceptions, models

file_name = ["data_3035_20220929.csv", "data_1205_20220930.csv"]
DB_CSV_DIR = "./resources/" + file_name[1]

SQL_APP_DB_ENGINE = database.engine


def main():
    new_stock_list = fetch_stocks(file_path=DB_CSV_DIR)
    upsert_stock(stock_list=new_stock_list, db=SQL_APP_DB_ENGINE)


def fetch_stocks(file_path: str):
    try:
        f = open(file_path, "r", encoding="euc-kr")
        csv_data_file = csv.reader(f)
        new_stock_list = []

        for line in csv_data_file:
            if line[0] == "종목코드":
                continue
            db_stock = models.Stock(
                code=line[0], market=line[2], name=line[1], price=int(line[4])
            )
            new_stock_list.append(db_stock)
        f.close()
        return new_stock_list
    except FileNotFoundError:
        raise exceptions.FileOpenError


def upsert_stock(stock_list: list[models.Stock], db: Engine):
    mapping_list = list(map(jsonable_encoder, stock_list))

    q = insert(models.Stock.__table__).values(mapping_list)

    with db.connect() as conn:
        conn.execute(
            q.on_conflict_do_update(
                index_elements=["code"],
                set_={
                    "price": q.excluded.price,
                },
            )
        )


if __name__ == "__main__":
    main()
