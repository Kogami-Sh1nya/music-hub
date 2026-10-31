from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload
from ..database import get_db
from ..models import Listen, Tag, Track, User
from ..schemas import TagsUpdate, TrackOut
from ..auth import current_user
from ..tag_utils import get_or_create_tags, normalize_tag, parse_tags

router = APIRouter(prefix="/api/tracks", tags=["tracks"])
MUSIC_DIR = Path(__file__).resolve().parents[2] / "media" / "music"
MUSIC_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED = {".mp3", ".wav", ".ogg", ".m4a"}

@router.get("", response_model=list[TrackOut])
def tracks(search: str = "", tag: str = "", db: Session = Depends(get_db)):
    q = db.query(Track).options(selectinload(Track.tags))
    search = search.strip()
    if search:
        s = f"%{search}%"
        # теги хранятся в нижнем регистре, поэтому ищем по lower-версии запроса
        q = q.filter(or_(
            Track.title.ilike(s), Track.artist.ilike(s), Track.album.ilike(s),
            Track.tags.any(Tag.name.like(f"%{search.lower()}%")),
        ))
    tag_name = normalize_tag(tag)
    if tag_name:
        q = q.filter(Track.tags.any(Tag.name == tag_name))
    return q.order_by(Track.uploaded_at.desc()).all()

@router.post("/upload", response_model=TrackOut)
def upload(title: str = Form(...), artist: str = Form(...), album: str = Form("Без альбома"), tags: str = Form(""), file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(current_user)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED: raise HTTPException(400, "Поддерживаются MP3, WAV, OGG и M4A")
    name = f"{uuid4().hex}{ext}"
    path = MUSIC_DIR / name
    with path.open("wb") as out:
        while chunk := file.file.read(1024 * 1024): out.write(chunk)
    track = Track(title=title.strip(), artist=artist.strip(), album=album.strip() or "Без альбома", filename=name)
    track.tags = get_or_create_tags(db, parse_tags(tags))
    db.add(track); db.commit(); db.refresh(track)
    return track

@router.put("/{track_id}/tags", response_model=TrackOut)
def set_tags(track_id: int, data: TagsUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Полностью заменяет набор тегов трека."""
    track = db.get(Track, track_id)
    if not track: raise HTTPException(404, "Трек не найден")
    track.tags = get_or_create_tags(db, parse_tags(data.tags))
    db.commit(); db.refresh(track)
    return track

@router.post("/{track_id}/listen")
def register_listen(track_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Фиксирует прослушивание — на этих данных строятся рекомендации."""
    if not db.get(Track, track_id): raise HTTPException(404, "Трек не найден")
    db.add(Listen(user_id=user.id, track_id=track_id)); db.commit()
    return {"ok": True}
