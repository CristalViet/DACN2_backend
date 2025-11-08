# 👤 9️⃣ app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150))
    role_id = Column(Integer, ForeignKey("user_roles.role_id"), nullable=True)
    date_joined = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)