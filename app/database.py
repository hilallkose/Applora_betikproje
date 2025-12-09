from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Senin PostgreSQL bağlantı adresin
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/database"

# Motoru (Engine) oluşturuyoruz
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Oturum oluşturucu (SessionLocal)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modellerin miras alacağı temel sınıf (Base)
Base = declarative_base()

# --- İŞTE EKSİK OLAN FONKSİYON ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()