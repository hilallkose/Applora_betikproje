import bcrypt
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

from app.database import SessionLocal, init_db
from app import models

# ===================================================
# FastAPI ve ayarlar
# ===================================================
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

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
        # Başarılı Giriş -> Profil sayfasına yönlendir (303 kodu ile)
        return RedirectResponse(url=f"/profile/{user.id}", status_code=status.HTTP_303_SEE_OTHER)
    
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
@app.get("/feed", response_class=HTMLResponse)
def feed(request: Request, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    if current_user_id is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    posts = db.query(models.Post).order_by(models.Post.created_at.desc()).all()
    return templates.TemplateResponse("feed.html", {"request": request, "posts": posts, "current_user_id": current_user_id})

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

# ===================================================
# Main
# ===================================================
if __name__ == "__main__":
    import uvicorn
    init_db()  # Tabloları oluştur
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


#uvicorn app.main:app --reload