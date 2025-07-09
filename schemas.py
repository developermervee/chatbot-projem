# schemas.py (Şifre Sıfırlama Şemaları Eklenmiş Tam Hali)

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# --- Token Şemaları ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

# --- Ürün Şemaları ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    owner_id: int
    class Config:
        from_attributes = True

# --- SSS Şemaları ---
class FaqBase(BaseModel):
    question: str
    answer: str

class FaqCreate(FaqBase):
    pass

class Faq(FaqBase):
    id: int
    owner_id: int
    class Config:
        from_attributes = True

# --- Potansiyel Müşteri (Lead) Şemaları ---
class LeadBase(BaseModel):
    customer_name: str
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None
    message: str

class LeadCreate(LeadBase):
    owner_id: int

class Lead(LeadBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- YENİ: ŞİFRE SIFIRLAMA ŞEMALARI ---
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
# --- YENİ BÖLÜM SONU ---

# --- Kullanıcı Şemaları ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    products: List[Product] = []
    faqs: List[Faq] = []
    leads: List[Lead] = []
    widget_color: Optional[str] = None
    welcome_message: Optional[str] = None
    
class Config:
    from_attributes = True

class UserUpdateSettings(BaseModel):
    widget_color: Optional[str] = None
    welcome_message: Optional[str] = None
    
# --- Chatbot Şemaları ---
class ChatRequest(BaseModel):
    message: str
    owner_id: int