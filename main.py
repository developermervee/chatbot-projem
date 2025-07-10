# main.py (TÜM ÖZELLİKLERİ İÇEREN NİHAİ, DOĞRU SIRALAMALI SÜRÜM)

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Merhaba dünya! Yenilendi 2025"}
