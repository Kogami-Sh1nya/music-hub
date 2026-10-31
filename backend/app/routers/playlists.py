from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth import current_user
from ..database import get_db
from ..models import Playlist, Track, User
from ..schemas import PlaylistCreate, PlaylistOut

router = APIRouter(prefix="/api/playlists", tags=["playlists"])

@router.get("", response_model=list[PlaylistOut])
def list_playlists(user: User = Depends(current_user)):
    return user.playlists

@router.post("", response_model=PlaylistOut)
def create_playlist(data: PlaylistCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    name = data.name.strip()
    if not name: raise HTTPException(400, "Введите название плейлиста")
    if len(name) > 100: raise HTTPException(400, "Название не длиннее 100 символов")
    if db.query(Playlist).filter(Playlist.owner_id == user.id, Playlist.name == name).first():
        raise HTTPException(400, "Плейлист с таким названием уже есть")
    p = Playlist(name=name, owner=user); db.add(p); db.commit(); db.refresh(p); return p

@router.delete("/{playlist_id}")
def delete_playlist(playlist_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(Playlist).filter(Playlist.id == playlist_id, Playlist.owner_id == user.id).first()
    if not p: raise HTTPException(404, "Плейлист не найден")
    db.delete(p); db.commit()
    return {"ok": True}

@router.post("/{playlist_id}/tracks/{track_id}")
def add_track(playlist_id: int, track_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(Playlist).filter(Playlist.id == playlist_id, Playlist.owner_id == user.id).first()
    track = db.get(Track, track_id)
    if not p or not track: raise HTTPException(404, "Плейлист или трек не найден")
    if track not in p.tracks: p.tracks.append(track); db.commit()
    return {"ok": True}

@router.delete("/{playlist_id}/tracks/{track_id}")
def remove_track(playlist_id: int, track_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(Playlist).filter(Playlist.id == playlist_id, Playlist.owner_id == user.id).first()
    track = db.get(Track, track_id)
    if p and track in p.tracks: p.tracks.remove(track); db.commit()
    return {"ok": True}
