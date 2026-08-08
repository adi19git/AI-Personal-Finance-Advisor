from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    icon = Column(String(50), nullable=True)  # emoji or icon class
    color = Column(String(7), nullable=True)  # hex color
    is_default = Column(Boolean, default=False)

    transactions = relationship("Transaction", back_populates="category")
