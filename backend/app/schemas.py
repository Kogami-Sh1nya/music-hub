from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TrackOut(BaseModel):
    id: int
    title: str
    artist: str
    album: str
    filename: str
    cover: str | None = None
    model_config = ConfigDict(from_attributes=True)

class PlaylistCreate(BaseModel):
    name: str

class PlaylistOut(BaseModel):
    id: int
    name: str
    tracks: list[TrackOut] = []
    model_config = ConfigDict(from_attributes=True)
