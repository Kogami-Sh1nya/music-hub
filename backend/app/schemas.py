from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TagOut(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class NameCount(BaseModel):
    name: str
    count: int

class TagsUpdate(BaseModel):
    tags: list[str] = []

class TrackOut(BaseModel):
    id: int
    title: str
    artist: str
    album: str
    filename: str
    cover: str | None = None
    tags: list[TagOut] = []
    model_config = ConfigDict(from_attributes=True)

class PlaylistCreate(BaseModel):
    name: str

class PlaylistOut(BaseModel):
    id: int
    name: str
    tracks: list[TrackOut] = []
    model_config = ConfigDict(from_attributes=True)

class AuthorOut(BaseModel):
    name: str
    tracks_count: int

class AuthorDetail(BaseModel):
    name: str
    tracks_count: int
    top_tags: list[NameCount] = []
    tracks: list[TrackOut] = []

class RecommendationsOut(BaseModel):
    has_history: bool
    top_tags: list[NameCount] = []
    top_artists: list[NameCount] = []
    tracks: list[TrackOut] = []

class RecentListen(BaseModel):
    played_at: datetime
    track: TrackOut

class ProfileOut(BaseModel):
    username: str
    created_at: datetime | None = None
    total_listens: int
    unique_tracks: int
    favorites_count: int
    playlists_count: int
    top_tags: list[NameCount] = []
    top_artists: list[NameCount] = []
    recent: list[RecentListen] = []

class PasswordChange(BaseModel):
    old_password: str
    new_password: str
