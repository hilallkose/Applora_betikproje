from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

# --- Veritabanı ve Modeller ---
from app.database import engine
from app import models

# --- Rotalarımızı (Böldüğümüz Dosyaları) Çağırıyoruz ---
from app.routes import auth, posts, likes, comments, relationships

# 1. Veritabanı Tablolarını Oluştur (Eğer yoksa)
models.Base.metadata.create_all(bind=engine)

# 2. Uygulamayı Başlat
app = FastAPI()

script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Bir üst klasör (Applora/)
parent_dir = os.path.dirname(script_dir)

# 3. Ana klasördeki "static" klasörünü hedefliyoruz
static_path = os.path.join(parent_dir, "static")

# 4. Bağlantıyı kuruyoruz
if not os.path.exists(static_path):
    os.makedirs(static_path)

app.mount("/static", StaticFiles(directory=static_path), name="static")

# 4. Rotaları (Router) Uygulamaya Dahil Et
# Artık login, register, post paylaşma vb. işlemleri bu dosyalardan çekecek
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(comments.router)
app.include_router(relationships.router)

# uvicorn app.main:app --reload
