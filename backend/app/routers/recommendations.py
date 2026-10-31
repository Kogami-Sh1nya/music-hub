from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..auth import current_user
from ..database import get_db
from ..models import User
from ..schemas import RecommendationsOut
from ..stats import artist_key, listening_stats

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

LIMIT = 20
ARTIST_WEIGHT = 2   # прослушивание трека автора весит как два совпадения по тегу

@router.get("", response_model=RecommendationsOut)
def recommendations(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """
    Подборка по истории прослушиваний:
      1. считаем, сколько раз пользователь слушал каждый тег (жанр) и каждого автора;
      2. оцениваем каждый трек: сумма «весов» его тегов + вес его автора;
      3. сначала показываем ещё не слышанные треки, затем уже знакомые — по убыванию оценки.
    """
    listened, tag_weight, artist_weight, artist_names, all_tracks = listening_stats(db, user.id)
    if not listened:
        return {"has_history": False, "top_tags": [], "top_artists": [], "tracks": []}

    scored = []
    for t in all_tracks:
        score = sum(tag_weight[tag.name] for tag in t.tags) + ARTIST_WEIGHT * artist_weight[artist_key(t.artist)]
        if score > 0:
            scored.append((t.id not in listened, score, t.uploaded_at or datetime.min, t))
    scored.sort(key=lambda x: x[:3], reverse=True)

    return {
        "has_history": True,
        "top_tags": [{"name": n, "count": c} for n, c in tag_weight.most_common(8)],
        "top_artists": [{"name": artist_names[k], "count": c} for k, c in artist_weight.most_common(5)],
        "tracks": [x[3] for x in scored[:LIMIT]],
    }
