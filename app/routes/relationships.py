from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

@router.post("/follow/{user_id}")
def follow_user(
    user_id: int, # Takip edilecek kişi
    current_user_id: int = Form(...), # Takip eden (Form'dan gelen gizli veri)
    db: Session = Depends(get_db)
):
    # Kendini takip etmeyi engelle
    if user_id == current_user_id:
        return RedirectResponse(url=f"/profile/{user_id}", status_code=status.HTTP_303_SEE_OTHER)

    # Zaten takip ediyor muyum?
    existing_follow = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user_id,
        models.Follow.followed_id == user_id
    ).first()

    if not existing_follow:
        new_follow = models.Follow(follower_id=current_user_id, followed_id=user_id)
        db.add(new_follow)
        db.commit()

    return RedirectResponse(url=f"/profile/{user_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/unfollow/{user_id}")
def unfollow_user(
    user_id: int, 
    current_user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    existing_follow = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user_id,
        models.Follow.followed_id == user_id
    ).first()

    if existing_follow:
        db.delete(existing_follow)
        db.commit()

    return RedirectResponse(url=f"/profile/{user_id}", status_code=status.HTTP_303_SEE_OTHER)