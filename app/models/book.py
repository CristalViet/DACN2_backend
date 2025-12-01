from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric, Text, Table
from app.database import Base
from sqlalchemy.orm import relationship

# Junction tables for many-to-many relationships
book_author = Table(
    'book_author',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id'), primary_key=True)
)

book_category = Table(
    'book_category',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    publisher_id = Column(Integer, ForeignKey("publishers.id"), nullable=True)
    title = Column(String(255), nullable=False)
    publish_date = Column(Date, nullable=True)
    cover_image = Column(String(500), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)

    # Many-to-many relationships
    authors = relationship("Author", secondary=book_author, back_populates="books")
    categories = relationship("Category", secondary=book_category, back_populates="books")
    
    # One-to-many relationships
    publisher = relationship("Publisher", back_populates="books")
    order_details = relationship("OrderDetail", back_populates="book")
    cart_items = relationship("CartItem", back_populates="book")
    summaries = relationship("Summary", back_populates="book")


