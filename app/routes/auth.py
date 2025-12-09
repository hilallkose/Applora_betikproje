from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import bcrypt

# Projenin diğer dosyalarından importlar
from app.database import get_db
from app import models

router = APIRouter()
# --------------------------------

templates = Jinja2Templates(directory="app/templates")

# --- Yardımcı Fonksiyonlar (Şifreleme) ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

# --- Rotalar ---
@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_post(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    hashed_pwd = hash_password(password)
    new_user = models.User(username=username, email=email, password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# auth.py dosyasının en altındaki login_post fonksiyonunu bununla değiştir:

@router.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if user and verify_password(password, user.password):
        # 1. Yönlendirmeyi hazırla
        response = RedirectResponse(url=f"/feed/{user.id}", status_code=status.HTTP_303_SEE_OTHER)
        
        # 2. Tarayıcıya "Kimlik Kartı" (Cookie) ver
        # Bu sayede diğer sayfalarda gezerken kim olduğunu unutmayacağız
        response.set_cookie(key="user_id", value=str(user.id))
        
        return response
    
    return templates.TemplateResponse("login.html", {"request": request, "message": "Geçersiz kimlik bilgileri"})

# --- ARAMA FONKSİYONU ---
@router.get("/search", response_class=HTMLResponse)
def search_users(
    request: Request, 
    q: str,  # Arama kutusuna yazılan kelime (query)
    db: Session = Depends(get_db)
):
    # Arama kutusu boşsa veya çok kısaysa bir şey yapma
    if not q or len(q) < 1:
        return RedirectResponse(url="/")
        
    # Veritabanında arama yap (küçük/büyük harf duyarsız olması için ilike kullanılır ama 
    # SQLite/Postgres farkı olmasın diye 'contains' kullanıyoruz)
    results = db.query(models.User).filter(models.User.username.contains(q)).all()
    
    # Cookie'den giriş yapan kullanıcıyı bul (Navbar için lazım)
    user_id = request.cookies.get("user_id")
    current_user = None
    if user_id:
        current_user = db.query(models.User).filter(models.User.id == int(user_id)).first()

    return templates.TemplateResponse("search.html", {
        "request": request, 
        "results": results, 
        "q": q,
        "user": current_user # Giriş yapmış kullanıcı bilgisi
    })
    
    # --- ÇIKIŞ YAPMA (LOGOUT) ---
@router.get("/logout")
def logout():
    # Kullanıcıyı giriş sayfasına yönlendir
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    # Tarayıcıdaki 'user_id' çerezini sil (Oturumu kapat)
    response.delete_cookie("user_id")
    
    return response