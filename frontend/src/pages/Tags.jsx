import {useEffect, useState} from "react";
import {useSearchParams} from "react-router-dom";
import api from "../api/api";
import TrackList from "../components/TrackList";
import useFavorites from "../hooks/useFavorites";
import {tracksWord} from "../utils";

export default function Tags() {
  const [params, setParams] = useSearchParams();
  const active = params.get("tag") || "";
  const [tags, setTags] = useState(null);
  const [tracks, setTracks] = useState([]);
  const fav = useFavorites();

  useEffect(() => { api.get("/tags").then(r => setTags(r.data)); }, []);
  useEffect(() => {
    if (!active) { setTracks([]); return; }
    api.get("/tracks", {params: {tag: active}}).then(r => setTracks(r.data));
  }, [active]);

  return (
    <section>
      <h1>Теги</h1>
      <p className="muted">Жанры, настроения и всё, что вы отметили у треков</p>
      {tags && !tags.length && <div className="empty">Тегов пока нет. Добавьте их при загрузке трека или через значок тегов у любого трека.</div>}
      <div className="tag-cloud">
        {(tags || []).map(t => (
          <button key={t.name} className={`tag-pill ${t.name === active ? "active" : ""}`} onClick={() => setParams(t.name === active ? {} : {tag: t.name})}>
            #{t.name} <span>{t.count}</span>
          </button>
        ))}
      </div>
      {active && <>
        <h2>#{active}</h2>
        <p className="muted">{tracksWord(tracks.length)}</p>
        {tracks.length ? <TrackList tracks={tracks} onFavorite={fav.toggle} favoriteIds={fav.ids}/> : <div className="empty">Нет треков с этим тегом</div>}
      </>}
    </section>
  );
}
