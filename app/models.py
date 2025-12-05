from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(128), nullable=False, unique=True, index=True)
    password = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- YENİ EKLENEN KISIM ---
    # Profil fotoğrafının dosya yolunu tutacak (Örn: /static/profile_images/resim.jpg)
    profile_image = Column(String, nullable=True) 
    # --------------------------

    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(255))
    caption = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"  # Tablo adı küçük ve çoğul

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ForeignKey'ler doğru tablo isimlerine (users, posts) bakmalı
    user_id = Column(Integer, ForeignKey("users.id")) 
    post_id = Column(Integer, ForeignKey("posts.id"))

    # İlişkiler
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    
    # DİKKAT: ForeignKey içindeki isimler veritabanındaki tablo adlarıyla AYNI olmalı
    user_id = Column(Integer, ForeignKey("users.id"))  # 'users' tablosuna
    post_id = Column(Integer, ForeignKey("posts.id"))  # 'posts' tablosuna

    # İlişkiler (Burada Sınıf isimlerini kullanıyoruz, o yüzden "User" ve "Post" kalabilir)
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")