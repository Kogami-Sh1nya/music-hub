from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .routers import auth, tracks, library, playlists, tags, authors, recommendations, profile

# create_all создаёт только отсутствующие таблицы (tags, track_tags, listens появятся сами)
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Music Hub API", version="1.1")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
MEDIA = Path(__file__).resolve().parents[1] / "media"
app.mount("/media", StaticFiles(directory=MEDIA), name="media")
for module in (auth, tracks, library, playlists, tags, authors, recommendations, profile):
    app.include_router(module.router)

@app.get("/api/health")
def health(): return {"status": "ok", "name": "Music Hub"}
