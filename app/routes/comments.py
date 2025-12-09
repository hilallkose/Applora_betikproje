from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

@router.post("/comment/{post_id}")
def add_comment(post_id: int, text: str = Form(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    new_comment = models.Comment(text=text, user_id=user_id, post_id=post_id)
    db.add(new_comment)
    db.commit()
    return RedirectResponse(url=f"/feed/{user_id}#post-{post_id}", status_code=status.HTTP_303_SEE_OTHER)