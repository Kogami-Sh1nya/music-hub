r"""
Загрузка демо-треков (без авторских прав, CC0) в Music Hub.

Запускать из папки backend, тем же Python, что и сервер:
    .\.venv\Scripts\python.exe seed_demo.py            # добавить демо-треки
    .\.venv\Scripts\python.exe seed_demo.py --remove   # удалить их

Скрипт можно запускать повторно: уже добавленные треки пропускаются.
Список треков, авторов и тегов лежит в demo_music/catalog.json.
"""
import json
import shutil
import sys
from pathlib import Path
from uuid import uuid4

from app.database import Base, SessionLocal, engine
from app.models import Track
from app.tag_utils import get_or_create_tags, parse_tags

BASE = Path(__file__).resolve().parent
DEMO_DIR = BASE / "demo_music"
MUSIC_DIR = BASE / "media" / "music"

def load_catalog():
    return json.loads((DEMO_DIR / "catalog.json").read_text(encoding="utf-8"))

def add():
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    added = 0
    with SessionLocal() as db:
        for item in load_catalog():
            src = DEMO_DIR / item["file"]
            if not src.exists():
                print(f"  нет файла {src.name} — пропускаю"); continue
            if db.query(Track).filter(Track.title == item["title"], Track.artist == item["artist"]).first():
                print(f"  уже есть: {item['artist']} — {item['title']}"); continue
            filename = f"{uuid4().hex}{src.suffix}"
            shutil.copy2(src, MUSIC_DIR / filename)
            track = Track(title=item["title"], artist=item["artist"], album=item["album"], filename=filename)
            track.tags = get_or_create_tags(db, parse_tags(item["tags"]))
            db.add(track); db.commit()
            added += 1
            print(f"  добавлен: {item['artist']} — {item['title']}")
    print(f"Готово, добавлено треков: {added}")

def remove():
    removed = 0
    with SessionLocal() as db:
        for item in load_catalog():
            track = db.query(Track).filter(Track.title == item["title"], Track.artist == item["artist"]).first()
            if not track: continue
            (MUSIC_DIR / track.filename).unlink(missing_ok=True)
            db.delete(track); db.commit()
            removed += 1
            print(f"  удалён: {item['artist']} — {item['title']}")
    print(f"Готово, удалено треков: {removed}")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    remove() if "--remove" in sys.argv else add()
