from collections import Counter
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload
from .models import Listen, Track

def artist_key(name: str) -> str:
    return (name or "").strip().casefold()

def listening_stats(db: Session, user_id: int):
    """
    Сводка по истории прослушиваний пользователя.
    Возвращает: listened {track_id: сколько раз}, tag_weight, artist_weight, artist_names, all_tracks.
    Используется и для рекомендаций, и для страницы профиля.
    """
    listened = dict(
        db.query(Listen.track_id, func.count(Listen.id))
        .filter(Listen.user_id == user_id)
        .group_by(Listen.track_id)
        .all()
    )
    all_tracks = db.query(Track).options(selectinload(Track.tags)).all()
    tag_weight: Counter = Counter()
    artist_weight: Counter = Counter()
    artist_names: dict[str, str] = {}
    for t in all_tracks:
        plays = listened.get(t.id)
        if not plays: continue
        key = artist_key(t.artist)
        artist_weight[key] += plays
        artist_names.setdefault(key, t.artist.strip())
        for tag in t.tags:
            tag_weight[tag.name] += plays
    return listened, tag_weight, artist_weight, artist_names, all_tracks
