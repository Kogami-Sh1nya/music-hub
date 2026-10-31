from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from ..database import get_db
from ..models import Track
from ..schemas import AuthorDetail, AuthorOut

router = APIRouter(prefix="/api/authors", tags=["authors"])

def author_key(name: str) -> str:
    # "Queen", "queen " и "QUEEN" — один автор
    return (name or "").strip().casefold()

@router.get("", response_model=list[AuthorOut])
def list_authors(search: str = "", db: Session = Depends(get_db)):
    groups: dict[str, dict] = {}
    for (artist,) in db.query(Track.artist).all():
        g = groups.setdefault(author_key(artist), {"name": artist.strip(), "tracks_count": 0})
        g["tracks_count"] += 1
    authors = list(groups.values())
    s = search.strip().casefold()
    if s:
        authors = [a for a in authors if s in a["name"].casefold()]
    return sorted(authors, key=lambda a: a["name"].casefold())

# имя передаётся query-параметром, а не частью пути: в названиях бывают "/", "?" и "#"
@router.get("/detail", response_model=AuthorDetail)
def author_detail(name: str, db: Session = Depends(get_db)):
    key = author_key(name)
    if not key: raise HTTPException(400, "Не указан автор")
    all_tracks = db.query(Track).options(selectinload(Track.tags)).order_by(Track.uploaded_at.desc()).all()
    tracks = [t for t in all_tracks if author_key(t.artist) == key]
    if not tracks: raise HTTPException(404, "Автор не найден")
    tag_counts = Counter(tag.name for t in tracks for tag in t.tags)
    return {
        "name": tracks[0].artist.strip(),
        "tracks_count": len(tracks),
        "top_tags": [{"name": n, "count": c} for n, c in tag_counts.most_common(8)],
        "tracks": tracks,
    }
