from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role_id = Column(Integer, ForeignKey("user_roles.id"), nullable=True)
    profile_image = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    date_joined = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    role = relationship("UserRole", back_populates="users")
    orders = relationship("Order", back_populates="user")
    summaries = relationship("Summary", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    cart = relationship("Cart", back_populates="user", uselist=False)