from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload
from ..auth import current_user, hash_password, verify_password
from ..database import get_db
from ..models import Listen, Playlist, Track, User, favorites
from ..schemas import PasswordChange, ProfileOut
from ..stats import listening_stats

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db), user: User = Depends(current_user)):
    listened, tag_weight, artist_weight, artist_names, _ = listening_stats(db, user.id)
    recent_rows = (
        db.query(Listen, Track)
        .join(Track, Track.id == Listen.track_id)
        .options(selectinload(Track.tags))
        .filter(Listen.user_id == user.id)
        .order_by(Listen.played_at.desc(), Listen.id.desc())
        .limit(30)
        .all()
    )
    return {
        "username": user.username,
        "created_at": user.created_at,
        "total_listens": sum(listened.values()),
        "unique_tracks": len(listened),
        "favorites_count": db.query(func.count()).select_from(favorites).filter(favorites.c.user_id == user.id).scalar() or 0,
        "playlists_count": db.query(func.count(Playlist.id)).filter(Playlist.owner_id == user.id).scalar() or 0,
        "top_tags": [{"name": n, "count": c} for n, c in tag_weight.most_common(8)],
        "top_artists": [{"name": artist_names[k], "count": c} for k, c in artist_weight.most_common(5)],
        "recent": [{"played_at": l.played_at, "track": t} for l, t in recent_rows],
    }

@router.put("/password")
def change_password(data: PasswordChange, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(400, "Неверный текущий пароль")
    if len(data.new_password) < 4:
        raise HTTPException(400, "Новый пароль — минимум 4 символа")
    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"ok": True}

@router.delete("/history")
def clear_history(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Очищает историю прослушиваний (а вместе с ней — основу рекомендаций)."""
    deleted = db.query(Listen).filter(Listen.user_id == user.id).delete(synchronize_session=False)
    db.commit()
    return {"ok": True, "deleted": deleted}
