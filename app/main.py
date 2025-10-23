from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
import app.models, app.schemas

app.models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Her istek için veritabanı bağlantısı
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Applora  API'ye hoş geldin!"}
