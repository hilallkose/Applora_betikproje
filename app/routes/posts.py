from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, status, UploadFile, File, Cookie # <-- Cookie Eklendi
from fastapi import APIRouter, Depends, Form, Request, status, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app import models
from app.services import image_service # Yazdığımız servisi kullanıyoruz!

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/feed/{user_id}", response_class=HTMLResponse)
def feed(request: Request, user_id: int, db: Session = Depends(get_db)):
    current_user = db.query(models.User).filter(models.User.id == user_id).first()
    posts = db.query(models.Post).join(models.User).order_by(desc(models.Post.created_at)).all()
    return templates.TemplateResponse("feed.html", {"request": request, "user": current_user, "posts": posts})

@router.get("/profile/{profile_id}", response_class=HTMLResponse)
def profile(
    request: Request, 
    profile_id: int, 
    db: Session = Depends(get_db),
    # Tarayıcıdaki kimlik kartını (Cookie) okuyoruz
    visitor_id: Optional[str] = Cookie(None, alias="user_id") 
):
    # Görüntülenecek profilin sahibi
    user = db.query(models.User).filter(models.User.id == profile_id).first()
    
    if not user:
        # Eğer böyle bir kullanıcı yoksa ana sayfaya dön (ama kimin ana sayfası?)
        # Cookie varsa ona dön, yoksa login'e at
        if visitor_id:
             return RedirectResponse(url=f"/feed/{visitor_id}")
        return RedirectResponse(url="/")

    # Ziyaretçi kendi profiline mi bakıyor?
    # Cookie'deki ID ile URL'deki ID aynı mı?
    is_owner = False
    if visitor_id and str(visitor_id) == str(profile_id):
        is_owner = True

    # Postları çek
    posts = db.query(models.Post).filter(models.Post.user_id == profile_id).order_by(desc(models.Post.created_at)).all()

    return templates.TemplateResponse("profile.html", {
        "request": request, 
        "user": user, 
        "posts": posts,
        "is_owner": is_owner, # Bu bilgiyi şablona gönderiyoruz!
        "visitor_id": visitor_id # Navbar'daki "Ana Sayfa" butonu için lazım
    })

@router.get("/upload/{user_id}", response_class=HTMLResponse)
def upload_get(request: Request, user_id: int):
    return templates.TemplateResponse("upload.html", {"request": request, "user_id": user_id})

@router.post("/upload/{user_id}")
def upload_post(user_id: int, caption: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Resmi servise gönderip kaydediyoruz
    saved_path = image_service.save_image(file, "images", file.filename)
    
    new_post = models.Post(user_id=user_id, image_path=saved_path, caption=caption)
    db.add(new_post)
    db.commit()
    return RedirectResponse(url=f"/profile/{user_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/delete_post/{post_id}")
def delete_post(post_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        # Önce dosyayı siliyoruz
        image_service.delete_image(post.image_path)
        # Sonra veritabanından siliyoruz
        db.delete(post)
        db.commit()
    return RedirectResponse(url=f"/profile/{user_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/update_profile_image/{user_id}")
async def update_profile_image(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        # Benzersiz isim oluştur
        ext = file.filename.split(".")[-1]
        filename = f"profile_{user_id}.{ext}"
        
        # Kaydet
        saved_path = image_service.save_image(file, "profile_images", filename)
        
        user.profile_image = saved_path
        db.commit()
    return RedirectResponse(url=f"/profile/{user_id}", status_code=status.HTTP_303_SEE_OTHER)