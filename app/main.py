import bcrypt
from fastapi.staticfiles import StaticFiles
from fastapi import File, UploadFile
import shutil
import os
from fastapi import FastAPI, Depends, Request, Form, File, UploadFile, status, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path
import shutil
import time
import traceback
from fastapi.staticfiles import StaticFiles
from app.database import SessionLocal, init_db
from app import models
from sqlalchemy import desc

# ===================================================
# FastAPI ve ayarlar
# ===================================================
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
# --- DÜZELTME BURADA BAŞLIYOR ---

# 1. main.py dosyasının nerede olduğunu buluyoruz
script_dir = os.path.dirname(os.path.abspath(__file__)) 

# 2. Bir üst klasöre (Applora klasörüne) çıkıyoruz
parent_dir = os.path.dirname(script_dir)

# 3. Oradaki "static" klasörünün tam yolunu oluşturuyoruz
static_path = os.path.join(parent_dir, "static")

# 4. static klasörünü bu tam yolla bağlıyoruz
app.mount("/static", StaticFiles(directory=static_path), name="static")

# --
# ===================================================
# Bağımlılıklar
# ===================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id(user_session: Optional[str] = Cookie(None)):
    if user_session is None:
        return None
    try:
        return int(user_session)
    except ValueError:
        return None

# ===================================================
# Şifreleme
# ===================================================
def hash_password(password: str) -> str:
    # Şifreyi byte'a çevirip hashliyoruz, sonra veritabanına kaydetmek için string'e (utf-8) dönüştürüyoruz
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Giriş yapılan şifreyle veritabanındaki hash'i karşılaştırıyoruz
    # checkpw ikisinin de byte olmasını ister, o yüzden encode ediyoruz
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False
# ===================================================
# Açık rotalar: Register / Login / Logout
# ===================================================
@app.get("/", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_page(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Şifreyi hashle
    hashed_pwd = hash_password(password)

    # Veritabanı modelini oluştur (models.User kullanıyoruz)
    new_user = models.User(
        username=username, 
        email=email, 
        password=hashed_pwd
    )

    # Veritabanına ekle ve kaydet
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # İşlem bitince ana sayfaya (Giriş ekranına) yönlendir
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/login")
def login_page(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    # 1. Önce sadece email ile kullanıcıyı veritabanından bul
    user = db.query(models.User).filter(models.User.email == email).first()
    
    # 2. Kullanıcı bulunduysa VE şifresi doğrulanıyorsa
    if user and verify_password(password, user.password):
    # ARTIK FEED'E GİDİYORUZ
     return RedirectResponse(url=f"/feed/{user.id}", status_code=status.HTTP_303_SEE_OTHER)
    
    # 3. Başarısız Giriş -> Kullanıcı yoksa veya şifre yanlışsa hata mesajı göster
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "message": "Geçersiz kimlik bilgileri"
    })

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="user_session")
    return response

# ===================================================
# Feed
# ===================================================
# --- FEED (ANA SAYFA) ENDPOINT ---
@app.get("/feed/{user_id}", response_class=HTMLResponse)
def feed(request: Request, user_id: int, db: Session = Depends(get_db)):
    
    # 1. Şu anki kullanıcıyı bul (Navbar'daki profil resmi ve ismi için)
    current_user = db.query(models.User).filter(models.User.id == user_id).first()
    
    # 2. TÜM postları çek (En yeniden en eskiye doğru sırala)
    # join(models.User) sayesinde postu atan kişinin bilgilerine de erişebileceğiz
    posts = db.query(models.Post).join(models.User).order_by(desc(models.Post.created_at)).all()
    
    return templates.TemplateResponse("feed.html", {
        "request": request, 
        "user": current_user, 
        "posts": posts
    })

# ===================================================
# Profil
# ===================================================
@app.get("/profile/{user_id}", response_class=HTMLResponse)
def profile(request: Request, user_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    if current_user_id is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/feed", status_code=status.HTTP_303_SEE_OTHER)
    user_posts = db.query(models.Post).filter(models.Post.user_id == user_id).order_by(models.Post.created_at.desc()).all()
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "posts": user_posts,
        "is_owner": current_user_id == user_id
    })

# ===================================================
# Yeni Post
# ===================================================
@app.get("/new_post", response_class=HTMLResponse)
def new_post_get(request: Request, current_user_id: int = Depends(get_current_user_id)):
    if current_user_id is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("new_post.html", {"request": request})

@app.post("/new_post")
def new_post_post(
    caption: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    if current_user_id is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    upload_folder = Path("app/static/uploads")
    upload_folder.mkdir(parents=True, exist_ok=True)
    safe_filename = f"{current_user_id}_{int(time.time())}_{file.filename}"
    file_path_on_disk = upload_folder / safe_filename
    try:
        with open(file_path_on_disk, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_path_for_db = f"/static/uploads/{safe_filename}"
        new_post = models.Post(user_id=current_user_id, image_path=image_path_for_db, caption=caption)
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return RedirectResponse(url="/feed", status_code=status.HTTP_303_SEE_OTHER)
    except Exception:
        traceback.print_exc()
        return RedirectResponse(url="/new_post", status_code=status.HTTP_303_SEE_OTHER)

# ===================================================
# Like
# ===================================================
@app.post("/like")
def add_like(post_id: int = Form(...), db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    if current_user_id is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    existing_like = db.query(models.Like).filter(models.Like.user_id == current_user_id, models.Like.post_id == post_id).first()
    if existing_like:
        db.delete(existing_like)
    else:
        db.add(models.Like(user_id=current_user_id, post_id=post_id))
    db.commit()
    return RedirectResponse(url="/feed", status_code=status.HTTP_303_SEE_OTHER)

# ===================================================
# Comment
# ===================================================
@app.post("/comment")
def add_comment(post_id: int = Form(...), comment_text: str = Form(...), db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    if current_user_id is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    if not comment_text.strip():
        return RedirectResponse(url="/feed", status_code=status.HTTP_303_SEE_OTHER)
    db.add(models.Comment(user_id=current_user_id, post_id=post_id, text=comment_text.strip()))
    db.commit()
    return RedirectResponse(url="/feed", status_code=status.HTTP_303_SEE_OTHER)


# 1. Yükleme Sayfasını Göster (GET)
@app.get("/upload/{user_id}", response_class=HTMLResponse)
def upload_get(request: Request, user_id: int):
    return templates.TemplateResponse("upload.html", {"request": request, "user_id": user_id})

# 2. Dosyayı Al ve Kaydet (POST)
@app.post("/upload/{user_id}")
def upload_post(
    request: Request,
    user_id: int,
    caption: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Klasör kontrolü (yoksa oluştur)
    if not os.path.exists("static/images"):
        os.makedirs("static/images")

    # Dosya ismini oluştur ve kaydet
    # (Çakışmayı önlemek için basitçe dosya adını kullanıyoruz, ileride uuid eklenebilir)
    file_location = f"static/images/{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Veritabanına Post olarak ekle
    # Not: Resim yolunu '/static/images/dosya_adi.jpg' olarak kaydediyoruz
    new_post = models.Post(
        user_id=user_id,
        image_path=f"/{file_location}", 
        caption=caption
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # İşlem bitince profil sayfasına geri dön
    return RedirectResponse(url=f"/profile/{user_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/update_profile_image")
async def update_profile_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Şu anki kullanıcıyı bulmamız lazım (Basitlik için cookie/session kullanmadığımızdan
    #    bu örnekte kullanıcı ID'sini formdan gizlice alacağız veya
    #    geçici olarak URL'den user_id isteyeceğiz. En kolayı URL'den almaktır.)
    #    FAKAT, form yapısı gereği user_id'yi form action'ına gömeceğiz.
    pass 

# DÜZELTME: Yukarıdaki fonksiyonu şu şekilde yazalım, user_id'yi URL'den alalım:
@app.post("/update_profile_image/{user_id}")
async def update_profile_image(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    # 2. Resmi Kaydet
    if not os.path.exists("static/profile_images"):
        os.makedirs("static/profile_images")
        
    # Dosya ismini unique yapmak için user_id kullanıyoruz
    # (Böylece her yeni yüklemede eski resmin üzerine yazar, yer kaplamaz)
    file_extension = file.filename.split(".")[-1]
    new_filename = f"profile_{user_id}.{file_extension}"
    file_location = f"static/profile_images/{new_filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 3. Veritabanını Güncelle
    # Veritabanına yolunu '/static/profile_images/...' olarak kaydediyoruz
    user.profile_image = f"/{file_location}"
    db.commit()
    db.refresh(user)
    
    return RedirectResponse(url=f"/profile/{user_id}", status_code=status.HTTP_303_SEE_OTHER)

# --- SİLME FONKSİYONU ---
@app.post("/delete_post/{post_id}")
def delete_post(
    post_id: int, 
    user_id: int = Form(...), # Silindikten sonra hangi profile döneceğimizi bilmek için
    db: Session = Depends(get_db)
):
    # 1. Silinecek postu bul
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if post:
        # 2. Önce bilgisayardaki dosyayı sil (Diskte yer kaplamasın)
        # Veritabanındaki yol "/static/..." diye başlar. Python dosyayı bulmak için
        # baştaki "/" işaretini istemez. Onu kaldırıyoruz (.lstrip).
        try:
            file_path = post.image_path.lstrip("/") 
            if os.path.exists(file_path):
                os.remove(file_path) # Dosyayı yok et 🗑️
        except Exception as e:
            print(f"Dosya silinirken hata: {e}")

        # 3. Şimdi veritabanından kaydı sil
        db.delete(post)
        db.commit()
    
    # İşlem bitince profil sayfasına geri dön
    return RedirectResponse(url=f"/profile/{user_id}", status_code=status.HTTP_303_SEE_OTHER)


# Bu fonksiyonu main.py'nin en altına ekle

@app.post("/like/{post_id}")
def toggle_like(
    post_id: int, 
    user_id: int = Form(...), # Hangi kullanıcı beğendi?
    db: Session = Depends(get_db)
):
    # 1. Bu kullanıcı bu postu daha önce beğenmiş mi?
    existing_like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == user_id
    ).first()

    if existing_like:
        # Zaten beğenmiş -> BEĞENİYİ GERİ AL (Sil)
        db.delete(existing_like)
    else:
        # Beğenmemiş -> BEĞENİ EKLE
        new_like = models.Like(user_id=user_id, post_id=post_id)
        db.add(new_like)
    
    db.commit()

    # İşlem bitince, kaldığımız yerden devam etmek için Feed sayfasına geri dön
    # (#post-{post_id} ekleyerek sayfada o postun olduğu hizaya gitmesini sağlıyoruz)
    return RedirectResponse(url=f"/feed/{user_id}#post-{post_id}", status_code=status.HTTP_303_SEE_OTHER)


# --- YORUM EKLEME ---
@app.post("/comment/{post_id}")
def add_comment(
    post_id: int,
    text: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Yeni yorum oluştur
    new_comment = models.Comment(
        text=text,
        user_id=user_id,
        post_id=post_id
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    # Yorum yapınca yine Feed sayfasına, o postun olduğu yere dön
    return RedirectResponse(url=f"/feed/{user_id}#post-{post_id}", status_code=status.HTTP_303_SEE_OTHER)


# ===================================================
# Main
# ===================================================
if __name__ == "__main__":
    import uvicorn
    init_db()  # Tabloları oluştur
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)




#uvicorn app.main:app --reload