from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Tag, track_tags
from ..schemas import NameCount

router = APIRouter(prefix="/api/tags", tags=["tags"])

@router.get("", response_model=list[NameCount])
def list_tags(db: Session = Depends(get_db)):
    """Все теги, которые назначены хотя бы одному треку, по убыванию популярности."""
    cnt = func.count(track_tags.c.track_id)
    rows = (db.query(Tag.name, cnt)
            .join(track_tags, track_tags.c.tag_id == Tag.id)
            .group_by(Tag.id, Tag.name)
            .order_by(cnt.desc(), Tag.name)
            .all())
    return [{"name": name, "count": count} for name, count in rows]
