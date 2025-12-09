from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

@router.post("/like/{post_id}")
def toggle_like(post_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    existing_like = db.query(models.Like).filter(models.Like.post_id == post_id, models.Like.user_id == user_id).first()
    if existing_like:
        db.delete(existing_like)
    else:
        new_like = models.Like(user_id=user_id, post_id=post_id)
        db.add(new_like)
    db.commit()
    return RedirectResponse(url=f"/feed/{user_id}#post-{post_id}", status_code=status.HTTP_303_SEE_OTHER)