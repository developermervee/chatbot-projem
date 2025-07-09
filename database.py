# database.py (Deployment'a Hazır Hali)

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Sunucuya yüklediğimizde, bize veritabanı adresini bu isimle bir "ortam değişkeni" olarak verecekler.
# Eğer o değişken varsa onu kullan, yoksa (yani kendi bilgisayarımızdaysak) sqlite dosyasını kullan.
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./chatbot.db")

# Bazı hosting servisleri "postgres://" ile başlayan adresler verir, 
# SQLAlchemy ise "postgresql://" bekler. Bu küçük kod, adresi uyumlu hale getirir.
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()