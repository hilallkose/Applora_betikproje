#sunucu başlatma
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import auth, posts, likes, comments

app = FastAPI(title="Applora")

# Yüklenen dosyaları servis et
app.mount("/uploads", StaticFiles(directory="static/uploads"), name="uploads")

# Router'ları dahil et
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(likes.router, prefix="/likes", tags=["Likes"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
