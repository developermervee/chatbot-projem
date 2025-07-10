# main.py (TÜM ÖZELLİKLERİ İÇEREN NİHAİ, DOĞRU SIRALAMALI SÜRÜM)

# Bu dosya, FastAPI uygulamasının ana dosyasıdır.

# 1. Önce tüm importlar
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
import pandas as pd
import io
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError
from typing import Annotated, List
from thefuzz import process

import models, schemas, security
from database import engine, get_db
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="frontend"), name="static")

# 2. Veritabanı tabloları oluşturulur
models.Base.metadata.create_all(bind=engine)

# 3. 'app' değişkeni burada, endpoint'lerden önce tanımlanır
app = FastAPI(
    title="KOBİ Chatbot Projesi API",
    description="Yönetici, Ürün, SSS, Lead ve Chatbot sistemi."
)

@app.get("/")
def read_root():
    return {"status": "OK", "message": "Chatbot API çalışıyor."}

# 4. CORS ayarları gibi Middleware'ler eklenir
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Ana Ayarlar ve Bağımlılık Fonksiyonları
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    """Token'ı doğrular ve mevcut kullanıcıyı döndürür."""
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None: raise credentials_exception
    return user


# 6. API Endpoint'leri (Tüm @app... fonksiyonları)

# --- KULLANICI YÖNETİMİ VE ŞİFRE SIFIRLAMA ---
@app.post("/register/", response_model=schemas.UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user: raise HTTPException(status_code=400, detail="Bu email adresi zaten kayıtlı.")
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user); db.commit(); db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Hatalı email veya şifre", headers={"WWW-Authenticate": "Bearer"})
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.UserInDB)
def read_users_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user

@app.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bu e-posta adresine sahip bir kullanıcı bulunamadı.")
    password_reset_token = security.create_password_reset_token(email=user.email)
    print("--- ŞİFRE SIFIRLAMA İSTEĞİ (SİMÜLASYON) ---")
    print(f"Kullanıcı: {user.email}")
    reset_file_path = r"file:///C:/Users/hp/chatbot2/frontend/reset-password.html"
    print(f"Sıfırlama Linki: {reset_file_path}?token={password_reset_token}")
    print("-----------------------------------------")
    return {"message": "Şifre sıfırlama talimatları e-posta adresinize gönderildi (Simülasyon)."}

@app.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(request: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    email = security.verify_password_reset_token(token=request.token)
    if not email: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz veya süresi dolmuş token.")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı.")
    hashed_password = security.get_password_hash(request.new_password)
    user.hashed_password = hashed_password
    db.commit()
    return {"message": "Şifreniz başarıyla güncellendi."}
@app.put("/users/me/settings", response_model=schemas.UserInDB)
def update_user_settings(
    settings: schemas.UserUpdateSettings,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Giriş yapmış kullanıcının chatbot kişiselleştirme ayarlarını günceller."""
    if settings.widget_color:
        current_user.widget_color = settings.widget_color
    if settings.welcome_message:
        current_user.welcome_message = settings.welcome_message
    
    db.commit()
    db.refresh(current_user)
    return current_user

# --- ÜRÜN YÖNETİMİ ---
@app.post("/products/", response_model=schemas.Product)
def create_product_for_user(product: schemas.ProductCreate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump(), owner_id=current_user.id)
    db.add(db_product); db.commit(); db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[schemas.Product])
def read_user_products(current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    return current_user.products
    
@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product( product_id: int, product_update: schemas.ProductCreate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.owner_id == current_user.id).first()
    if not db_product: raise HTTPException(status_code=404, detail="Güncellenecek ürün bulunamadı.")
    for key, value in product_update.model_dump().items():
        setattr(db_product, key, value)
    db.commit(); db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    product_to_delete = db.query(models.Product).filter(models.Product.id == product_id, models.Product.owner_id == current_user.id).first()
    if not product_to_delete: raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    db.delete(product_to_delete); db.commit()
    return

@app.post("/upload-products/", response_model=dict)
async def upload_products_from_file(file: UploadFile, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    file_extension = file.filename.split('.')[-1].lower() if file.filename else ""
    if file_extension not in ['csv', 'xlsx']: raise HTTPException(status_code=400, detail="Geçersiz dosya formatı. Lütfen .csv veya .xlsx dosyası yükleyin.")
    try:
        contents = await file.read()
        if file_extension == 'csv': df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        else: df = pd.read_excel(io.BytesIO(contents))
        df.columns = [col.lower().strip() for col in df.columns]
        required_columns = {'name', 'price'}
        if not required_columns.issubset(df.columns): raise HTTPException(status_code=400, detail="Dosyada 'name' ve 'price' sütunları zorunludur.")
        new_products = []
        for _, row in df.iterrows():
            description = row.get('description', None)
            if pd.isna(description): description = None
            product_data = models.Product(name=row['name'], description=description, price=row['price'], owner_id=current_user.id)
            new_products.append(product_data)
        db.add_all(new_products); db.commit()
        return {"message": f"{len(new_products)} adet ürün başarıyla eklendi."}
    except Exception as e:
        db.rollback(); raise HTTPException(status_code=500, detail=f"Dosya işlenirken bir hata oluştu: {e}")

# --- SSS YÖNETİMİ ---
@app.post("/faqs/", response_model=schemas.Faq)
def create_faq_for_user(faq: schemas.FaqCreate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_faq = models.Faq(**faq.model_dump(), owner_id=current_user.id)
    db.add(db_faq); db.commit(); db.refresh(db_faq)
    return db_faq

@app.get("/faqs/", response_model=List[schemas.Faq])
def read_user_faqs(current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    return current_user.faqs

@app.delete("/faqs/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faq(faq_id: int, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    faq_to_delete = db.query(models.Faq).filter(models.Faq.id == faq_id, models.Faq.owner_id == current_user.id).first()
    if not faq_to_delete: raise HTTPException(status_code=404, detail="SSS bulunamadı.")
    db.delete(faq_to_delete); db.commit()
    return

# --- POTANSİYEL MÜŞTERİ (LEAD) YÖNETİMİ ---
@app.post("/leads/", response_model=schemas.Lead, status_code=status.HTTP_201_CREATED)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    owner = db.query(models.User).filter(models.User.id == lead.owner_id).first()
    if not owner: raise HTTPException(status_code=404, detail="Belirtilen sahip (owner) bulunamadı.")
    db_lead = models.Lead(**lead.model_dump()); db.add(db_lead); db.commit(); db.refresh(db_lead)
    return db_lead

@app.get("/leads/", response_model=List[schemas.Lead])
def read_user_leads(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user.leads

# --- CHATBOT ---
@app.post("/chat")
def handle_chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    user_message = request.message.lower()
    owner_products = db.query(models.Product).filter(models.Product.owner_id == request.owner_id).all()
    owner_faqs = db.query(models.Faq).filter(models.Faq.owner_id == request.owner_id).all()
    
    product_choices = {p.name: p for p in owner_products}
    if product_choices:
        best_product_match = process.extractOne(user_message, product_choices.keys())
        if best_product_match and best_product_match[1] > 80:
            matched_product = product_choices[best_product_match[0]]
            response_text = (f"Sanırım '{matched_product.name}' ürününü soruyorsunuz. Fiyatı {matched_product.price} TL. Ürün açıklaması: {matched_product.description}")
            return {"response": response_text}
            
    faq_choices = {f.question: f for f in owner_faqs}
    if faq_choices:
        best_faq_match = process.extractOne(user_message, faq_choices.keys())
        if best_faq_match and best_faq_match[1] > 80:
            matched_faq = faq_choices[best_faq_match[0]]
            return {"response": matched_faq.answer}
            
    if "kargo" in user_message or "teslimat" in user_message:
        return {"response": "Tüm Türkiye'ye kargo ücretimiz 50 TL'dir. 1000 TL ve üzeri alışverişlerde kargo ücretsizdir."}
    if "merhaba" in user_message or "selam" in user_message:
        return {"response": "Merhaba! Size nasıl yardımcı olabilirim?"}
    return {"response": "Üzgünüm, sorunuzu tam olarak anlayamadım. İsterseniz iletişim bilgilerinizi bırakın, size en kısa sürede ulaşalım.", "type": "lead_capture"}