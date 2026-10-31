from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

playlist_tracks = Table(
    "playlist_tracks", Base.metadata,
    Column("playlist_id", ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True),
    Column("track_id", ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True),
)

favorites = Table(
    "favorites", Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("track_id", ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True),
)

track_tags = Table(
    "track_tags", Base.metadata,
    Column("track_id", ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    playlists = relationship("Playlist", back_populates="owner", cascade="all, delete-orphan")
    favorite_tracks = relationship("Track", secondary=favorites, back_populates="liked_by")

class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False, index=True)
    artist = Column(String(150), nullable=False, index=True)
    album = Column(String(150), default="Без альбома")
    filename = Column(String(255), unique=True, nullable=False)
    cover = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    liked_by = relationship("User", secondary=favorites, back_populates="favorite_tracks")
    playlists = relationship("Playlist", secondary=playlist_tracks, back_populates="tracks")
    tags = relationship("Tag", secondary=track_tags, back_populates="tracks", order_by="Tag.name")

class Tag(Base):
    """Тег трека: жанр (рок, джаз), настроение (грустное, для спорта) и т.д."""
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True, nullable=False, index=True)
    tracks = relationship("Track", secondary=track_tags, back_populates="tags")

class Listen(Base):
    """Одно прослушивание трека пользователем. По этим записям строятся рекомендации."""
    __tablename__ = "listens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False, index=True)
    played_at = Column(DateTime, default=datetime.utcnow)

class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="playlists")
    tracks = relationship("Track", secondary=playlist_tracks, back_populates="playlists")
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_owner_playlist_name"),)
