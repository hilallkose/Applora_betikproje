
from sqlalchemy import Column, Integer, CHAR, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    username = Column(CHAR)
    email = Column(CHAR)
    password = Column(CHAR)
    created_at = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = "Post"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("User.id"))
    image_path = Column(CHAR)
    caption = Column(CHAR)
    created_at = Column(DateTime, default=datetime.utcnow)

class Like(Base):
    __tablename__="Like"
    id = Column(Integer, primary_key=True)
    user_id=Column(Integer, ForeignKey("User.id"))
    post_id=Column(Integer, ForeignKey("Post.id"))
    
class Comment(Base):
    __tablename__="Comment"
    id = Column(Integer, primary_key=True)
    user_id=Column(Integer, ForeignKey("User.id"))
    post_id=Column(Integer, ForeignKey("Post.id"))
    text=Column(CHAR)
    created_at = Column(DateTime, default=datetime.utcnow)