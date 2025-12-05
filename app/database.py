from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app import models  # models.py içindeki Base ve modeller

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/database"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = models.Base  # models.py içindeki Base kullanıyoruz

def init_db():
    Base.metadata.create_all(bind=engine)
