from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(128), nullable=False, unique=True, index=True)
    password = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    profile_image = Column(String, nullable=True) 

    # İlişkiler
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")

    # Takip İlişkileri (Foreign Key ayarları kritik)
    following = relationship("Follow", foreign_keys="[Follow.follower_id]", back_populates="follower")
    followers = relationship("Follow", foreign_keys="[Follow.followed_id]", back_populates="followed")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_path = Column(String)
    caption = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # İlişkiler
    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

class Follow(Base):
    __tablename__ = "follows"

    # --- KRİTİK DÜZELTME: Primary Key Eklendi ---
    id = Column(Integer, primary_key=True, index=True)
    # --------------------------------------------

    follower_id = Column(Integer, ForeignKey("users.id")) # Takip eden
    followed_id = Column(Integer, ForeignKey("users.id")) # Takip edilen

    # İlişkiler
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers")