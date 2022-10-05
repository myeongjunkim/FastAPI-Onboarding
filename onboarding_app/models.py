from sqlalchemy import Boolean, Column, Integer, String

from onboarding_app.database import Base, engine


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, index=True)
    market = Column(String, index=True)
    name = Column(String, index=True)
    price = Column(Integer, index=True, default=0)


User.__table__.create(bind=engine, checkfirst=True)
Stock.__table__.create(bind=engine, checkfirst=True)
