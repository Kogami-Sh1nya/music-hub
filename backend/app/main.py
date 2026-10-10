
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .routers import auth, tracks, library, playlists

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Music Hub API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
MEDIA = Path(__file__).resolve().parents[1] / "media"
app.mount("/media", StaticFiles(directory=MEDIA), name="media")
app.include_router(auth.router); app.include_router(tracks.router); app.include_router(library.router); app.include_router(playlists.router)

@app.get("/api/health")
def health(): return {"status": "ok", "name": "Music Hub"}
