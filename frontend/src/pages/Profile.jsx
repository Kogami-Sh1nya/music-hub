import {useCallback, useEffect, useState} from "react";
import {Link} from "react-router-dom";
import api from "../api/api";
import TrackList from "../components/TrackList";
import TagChips from "../components/TagChips";
import useFavorites from "../hooks/useFavorites";
import {authorLink, formatDate, timeAgo} from "../utils";

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  const [form, setForm] = useState({old_password: "", new_password: ""});
  const [pwMsg, setPwMsg] = useState({type: "", text: ""});
  const fav = useFavorites();

  const load = useCallback(() =>
    api.get("/profile")
      .then(r => { setProfile(r.data); setError(""); })
      .catch(err => setError(err.response?.data?.detail || "Не удалось загрузить профиль")),
  []);
  useEffect(() => { load(); }, [load]);

  const changePassword = async e => {
    e.preventDefault(); setPwMsg({type: "", text: ""});
    try {
      await api.put("/profile/password", form);
      setForm({old_password: "", new_password: ""});
      setPwMsg({type: "ok", text: "Пароль изменён"});
    } catch (err) {
      setPwMsg({type: "err", text: err.response?.data?.detail || "Не удалось изменить пароль"});
    }
  };
  const clearHistory = async () => {
    if (!window.confirm("Очистить историю прослушиваний? Рекомендации начнутся с нуля.")) return;
    await api.delete("/profile/history");
    load();
  };

  if (error) return <section><h1>Профиль</h1><div className="alert alert-danger py-2">{error}</div></section>;
  if (!profile) return <section><h1>Профиль</h1></section>;

  // в истории один трек может встречаться много раз — оставляем последнее прослушивание
  const seen = new Set();
  const recent = profile.recent.filter(r => !seen.has(r.track.id) && seen.add(r.track.id)).slice(0, 10);
  const playedAt = Object.fromEntries(recent.map(r => [r.track.id, r.played_at]));
  const stats = [
    ["bi-headphones", profile.total_listens, "прослушиваний"],
    ["bi-music-note-beamed", profile.unique_tracks, "разных треков"],
    ["bi-heart", profile.favorites_count, "в избранном"],
    ["bi-music-note-list", profile.playlists_count, "плейлистов"],
  ];

  return (
    <section>
      <div className="author-head">
        <div className="author-avatar big">{profile.username.charAt(0).toUpperCase()}</div>
        <div>
          <span className="eyebrow">ПРОФИЛЬ</span>
          <h1>{profile.username}</h1>
          {profile.created_at && <p className="muted mb-0">В Music Hub с {formatDate(profile.created_at)}</p>}
        </div>
      </div>

      <div className="stat-grid">
        {stats.map(([icon, value, label]) => (
          <div className="stat-card" key={label}>
            <i className={`bi ${icon}`}/>
            <strong>{value}</strong>
            <span>{label}</span>
          </div>
        ))}
      </div>

      <h2>Ваш вкус</h2>
      {profile.total_listens === 0
        ? <div className="empty">Здесь появятся любимые жанры и авторы, как только вы послушаете несколько треков.</div>
        : <div className="rec-meta">
            <div><span className="rec-label">Любимые теги</span>{profile.top_tags.length ? <TagChips tags={profile.top_tags}/> : <span className="muted"> — у прослушанных треков нет тегов</span>}</div>
            <div><span className="rec-label">Любимые авторы</span>
              <div className="tag-chips">{profile.top_artists.map(a => <Link key={a.name} className="tag-chip" to={authorLink(a.name)}>{a.name} · {a.count}</Link>)}</div>
            </div>
          </div>}

      {recent.length > 0 && <>
        <h2 className="mt-5">Недавно слушали</h2>
        <TrackList tracks={recent.map(r => r.track)} onFavorite={fav.toggle} favoriteIds={fav.ids}
          extra={t => <span className="played-at">{timeAgo(playedAt[t.id])}</span>}/>
      </>}

      <h2 className="mt-5">Настройки</h2>
      <div className="settings-grid">
        <form className="settings-card" onSubmit={changePassword}>
          <h3>Смена пароля</h3>
          <input className="form-control" type="password" placeholder="Текущий пароль" required value={form.old_password} onChange={e => setForm({...form, old_password: e.target.value})}/>
          <input className="form-control" type="password" placeholder="Новый пароль (минимум 4 символа)" required value={form.new_password} onChange={e => setForm({...form, new_password: e.target.value})}/>
          <button className="btn btn-primary">Изменить пароль</button>
          {pwMsg.text && <div className={pwMsg.type === "ok" ? "pl-msg" : "pl-error"}>{pwMsg.text}</div>}
        </form>
        <div className="settings-card">
          <h3>История прослушиваний</h3>
          <p className="muted">Рекомендации строятся по ней. Если подборка стала скучной, историю можно сбросить.</p>
          <button className="btn btn-outline-danger" onClick={clearHistory} disabled={profile.total_listens === 0}>Очистить историю</button>
        </div>
      </div>
    </section>
  );
}
