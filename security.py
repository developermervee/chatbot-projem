# security.py (Şifre Sıfırlama Mantığı Eklenmiş Tam Hali)

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# Şifre hashleme için context'i oluşturuyoruz
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- GÜVENLİK ANAHTARLARI ---
# Bu anahtarları gizli tutmak çok önemlidir.
# Normalde bunları bir ortam değişkeninden (environment variable) okuruz.
SECRET_KEY = "bunu_mutlaka_degistir_cok_gizli_bir_anahtar"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# YENİ: Şifre sıfırlama için ayrı ve daha kısa ömürlü bir ayar
PASSWORD_RESET_SECRET_KEY = "bu_da_farkli_ve_gizli_bir_sifirlama_anahtari"
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 15

# --- ŞİFRELEME FONKSİYONLARI ---

def verify_password(plain_password, hashed_password):
    """Girilen şifre ile hash'lenmiş şifreyi karşılaştırır."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Verilen şifreyi hash'ler."""
    return pwd_context.hash(password)

# --- NORMAL GİRİŞ TOKEN'I FONKSİYONLARI ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Normal giriş için kullanılan JWT (access token) oluşturur."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- YENİ: ŞİFRE SIFIRLAMA TOKEN'I FONKSİYONLARI ---

def create_password_reset_token(email: str) -> str:
    """Şifre sıfırlama için özel, kısa ömürlü bir token oluşturur."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": email}
    encoded_jwt = jwt.encode(to_encode, PASSWORD_RESET_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """Şifre sıfırlama token'ını doğrular ve içindeki e-postayı döndürür."""
    try:
        decoded_token = jwt.decode(token, PASSWORD_RESET_SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token.get("sub")
    except JWTError:
        return None