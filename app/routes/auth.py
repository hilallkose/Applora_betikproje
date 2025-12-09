from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import bcrypt

# Projenin diğer dosyalarından importlar
from app.database import get_db
from app import models

# --- İŞTE EKSİK OLAN SATIR BU ---
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

@router.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user and verify_password(password, user.password):
        return RedirectResponse(url=f"/feed/{user.id}", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {"request": request, "message": "Geçersiz kimlik bilgileri"})