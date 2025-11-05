from urllib import request
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from fastapi import status
from app import models

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/profile/{user_id}", response_class=HTMLResponse)
def profile(request: Request, user_id: int, db: Session = Depends(get_db)): 
    
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("profile.html", {
        "request": request, 
        "user_id": user_id, 
        "user": user,
    })

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
 return templates.TemplateResponse("login.html", {"request": request})
@app.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_page(db: Session = Depends(get_db)):


    new_user = models.User(username="username", email="email", password="password")
    
    db.add(new_user) 
    db.commit()
    
    db.refresh(new_user) 

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/login")
def login_page( db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == "email", models.User.password == "password").first()
    
    if user:
        return RedirectResponse(url=f"/profile/{user.id}", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("login.html", {"request": request,"message":"Geçersiz kimlik bilgileri"})
   

#uvicorn app.main:app --reload