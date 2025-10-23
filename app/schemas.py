from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class PostCreate(BaseModel):
    caption: str
    image_path: str

class CommentCreate(BaseModel):
    post_id: int
    text: str
