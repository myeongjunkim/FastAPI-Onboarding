from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from onboarding_app.database import Base, engine


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    wishlists = relationship("Wishlist", backref="user")


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, index=True)
    market = Column(String, index=True)
    name = Column(String, index=True)
    price = Column(Integer, index=True, default=0)


class Wishlist(Base):
    __tablename__ = "wishlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, index=True)
    __table_args__ = (UniqueConstraint("user_id", "name", name="user_id__name_unique"),)

    description = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    is_open = Column(Boolean, default=False)
    order_num = Column(Integer, nullable=True)


class WishlistXstock(Base):
    __tablename__ = "wishlist_x_stock"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wishlist_id = Column(Integer, ForeignKey("wishlists.id", ondelete="CASCADE"))
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"))
    __table_args__ = (
        UniqueConstraint(
            "wishlist_id", "stock_id", name="wishlist_id__stock_id_unique"
        ),
    )

    purchase_price = Column(Integer, nullable=True)
    holding_num = Column(Integer, nullable=True)
    order_num = Column(Integer, nullable=True)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    wishlist_id = Column(Integer, ForeignKey("wishlists.id", ondelete="CASCADE"))
    body = Column(String)
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))
    is_reply = Column(Boolean)

    # reply = relationship("Comment", backref="reply")


class History(Base):
    __tablename__ = "historys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))
    body = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


User.__table__.create(bind=engine, checkfirst=True)
Stock.__table__.create(bind=engine, checkfirst=True)
Wishlist.__table__.create(bind=engine, checkfirst=True)
WishlistXstock.__table__.create(bind=engine, checkfirst=True)
Comment.__table__.create(bind=engine, checkfirst=True)
History.__table__.create(bind=engine, checkfirst=True)
