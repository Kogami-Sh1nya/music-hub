from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Track, User
from ..schemas import TrackOut
from ..auth import current_user

router = APIRouter(prefix="/api/tracks", tags=["tracks"])
MUSIC_DIR = Path(__file__).resolve().parents[2] / "media" / "music"
MUSIC_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED = {".mp3", ".wav", ".ogg", ".m4a"}

@router.get("", response_model=list[TrackOut])
def tracks(search: str = "", db: Session = Depends(get_db)):
    q = db.query(Track)
    if search:
        s = f"%{search}%"
        q = q.filter(or_(Track.title.ilike(s), Track.artist.ilike(s), Track.album.ilike(s)))
    return q.order_by(Track.uploaded_at.desc()).all()

@router.post("/upload", response_model=TrackOut)
def upload(title: str = Form(...), artist: str = Form(...), album: str = Form("Без альбома"), file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(current_user)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED: raise HTTPException(400, "Поддерживаются MP3, WAV, OGG и M4A")
    name = f"{uuid4().hex}{ext}"
    path = MUSIC_DIR / name
    with path.open("wb") as out:
        while chunk := file.file.read(1024 * 1024): out.write(chunk)
    track = Track(title=title.strip(), artist=artist.strip(), album=album.strip() or "Без альбома", filename=name)
    db.add(track); db.commit(); db.refresh(track)
    return track
