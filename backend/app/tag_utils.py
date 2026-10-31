import re
from sqlalchemy.orm import Session
from .models import Tag

MAX_TAGS_PER_TRACK = 10
MAX_TAG_LENGTH = 30

def normalize_tag(raw: str) -> str:
    """'  #Рок  Н Ролл ' -> 'рок н ролл'"""
    name = re.sub(r"\s+", " ", (raw or "").strip().lstrip("#").strip()).lower()
    return name[:MAX_TAG_LENGTH].strip()

def parse_tags(values) -> list[str]:
    """Принимает строку 'рок, джаз' или список строк. Возвращает уникальные нормализованные теги."""
    if isinstance(values, str):
        values = values.split(",")
    result: list[str] = []
    for value in values or []:
        name = normalize_tag(value)
        if name and name not in result:
            result.append(name)
    return result[:MAX_TAGS_PER_TRACK]

def get_or_create_tags(db: Session, names: list[str]) -> list[Tag]:
    if not names:
        return []
    existing = {t.name: t for t in db.query(Tag).filter(Tag.name.in_(names)).all()}
    tags = []
    for name in names:
        tag = existing.get(name)
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
            existing[name] = tag
        tags.append(tag)
    return tags
