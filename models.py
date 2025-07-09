# models.py (Nihai Tam Hali)

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    products = relationship("Product", back_populates="owner")
    faqs = relationship("Faq", back_populates="owner")
    leads = relationship("Lead", back_populates="owner")
# --- DÜZELTME BURADA ---
    # widget_color kaldırıldı, yerine veritabanıyla uyumlu olan widget_theme eklendi.
    widget_theme = Column(String, default="light")
    welcome_message = Column(String, default="Merhaba! Size nasıl yardımcı olabilirim?")
    # --- DÜZELTME SONU --
    products = relationship("Product", back_populates="owner")
    faqs = relationship("Faq", back_populates="owner")
    leads = relationship("Lead", back_populates="owner")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="products")

class Faq(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True, nullable=False)
    answer = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="faqs")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    customer_email = Column(String, index=True, nullable=True)
    customer_phone = Column(String, nullable=True)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="leads")