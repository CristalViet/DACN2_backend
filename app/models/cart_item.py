from sqlalchemy import Column, Integer, ForeignKey, Numeric
from app.database import Base
from sqlalchemy.orm import relationship


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    cart = relationship("Cart", back_populates="cart_items")
    book = relationship("Book", back_populates="cart_items")

