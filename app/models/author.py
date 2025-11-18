from sqlalchemy import Column, Integer, String, Date, Text
from app.database import Base
from sqlalchemy.orm import relationship


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=True)
    nationality = Column(String(100), nullable=True)
    biography = Column(Text, nullable=True)

    books = relationship("Book", back_populates="author")


