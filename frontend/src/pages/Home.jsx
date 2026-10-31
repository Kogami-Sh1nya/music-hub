import {useEffect, useState} from "react";
import {Link} from "react-router-dom";
import api from "../api/api";
import TrackList from "../components/TrackList";
import TagChips from "../components/TagChips";
import useFavorites from "../hooks/useFavorites";
import {authorLink} from "../utils";

export default function Home() {
  const [tracks, setTracks] = useState([]);
  const [rec, setRec] = useState(null);
  const fav = useFavorites();

  useEffect(() => {
    api.get('/tracks').then(r => setTracks(r.data));
    api.get('/recommendations').then(r => setRec(r.data)).catch(() => {});
  }, []);

  return <>
    <div className="hero"><div><span className="eyebrow">ДОБРО ПОЖАЛОВАТЬ</span><h1>Вся музыка в одном месте</h1><p>Загружай композиции, собирай библиотеку и слушай любимые треки.</p></div><i className="bi bi-headphones hero-icon"/></div>

    <section>
      <h2>Подобрано для вас</h2>
      {rec && !rec.has_history && <div className="empty">Послушайте несколько треков — и здесь появится подборка по вашим любимым жанрам и авторам.</div>}
      {rec?.has_history && <>
        <div className="rec-meta">
          <div><span className="rec-label">Любимые теги</span>{rec.top_tags.length ? <TagChips tags={rec.top_tags}/> : <span className="muted"> — пока нет, добавьте теги трекам</span>}</div>
          <div><span className="rec-label">Любимые авторы</span>
            <div className="tag-chips">{rec.top_artists.map(a => <Link key={a.name} className="tag-chip" to={authorLink(a.name)}>{a.name}</Link>)}</div>
          </div>
        </div>
        {rec.tracks.length
          ? <TrackList tracks={rec.tracks} onFavorite={fav.toggle} favoriteIds={fav.ids}/>
          : <div className="empty">Пока нечего предложить. Загрузите больше музыки или добавьте теги трекам.</div>}
      </>}
    </section>

    <section className="mt-5"><h2>Последние треки</h2>{tracks.length ? <TrackList tracks={tracks} onFavorite={fav.toggle} favoriteIds={fav.ids}/> : <div className="empty">Музыки пока нет. Загрузите первый трек.</div>}</section>
  </>;
}
