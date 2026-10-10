from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth import current_user
from ..database import get_db
from ..models import Track, User
from ..schemas import TrackOut

router = APIRouter(prefix="/api/favorites", tags=["favorites"])

@router.get("", response_model=list[TrackOut])
def get_favorites(user: User = Depends(current_user)):
    return user.favorite_tracks

@router.post("/{track_id}")
def add_favorite(track_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    track = db.get(Track, track_id)
    if not track: raise HTTPException(404, "Трек не найден")
    if track not in user.favorite_tracks: user.favorite_tracks.append(track); db.commit()
    return {"ok": True}

@router.delete("/{track_id}")
def remove_favorite(track_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    track = db.get(Track, track_id)
    if track in user.favorite_tracks: user.favorite_tracks.remove(track); db.commit()
    return {"ok": True}
