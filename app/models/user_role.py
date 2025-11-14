from sqlalchemy import Column, Integer, String, Text
from app.database import Base
from sqlalchemy.orm import relationship


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    permissions = Column(Text, nullable=True)

    users = relationship("User", back_populates="role")


