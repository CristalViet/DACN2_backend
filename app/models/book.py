from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric, Text
from app.database import Base
from sqlalchemy.orm import relationship


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=True)
    publisher_id = Column(Integer, ForeignKey("publishers.id"), nullable=True)
    title = Column(String(255), nullable=False)
    publish_date = Column(Date, nullable=True)
    cover_image = Column(String(500), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)

    category = relationship("Category", back_populates="books")
    author = relationship("Author", back_populates="books")
    publisher = relationship("Publisher", back_populates="books")
    order_details = relationship("OrderDetail", back_populates="book")
    cart_items = relationship("CartItem", back_populates="book")


