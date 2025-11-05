from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class PostCreate(BaseModel):
    caption: str
    image_path: str

class CommentCreate(BaseModel):
    username: str
    post_id: int
    text: str
class LikeCreate(BaseModel):
    post_id: int
