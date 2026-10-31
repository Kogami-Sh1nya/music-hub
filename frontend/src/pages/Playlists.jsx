import {useEffect, useState} from "react";
import api from "../api/api";
import TrackList from "../components/TrackList";
import {tracksWord} from "../utils";

export default function Playlists() {
  const [lists, setLists] = useState(null), [name, setName] = useState(''), [tracks, setTracks] = useState([]), [error, setError] = useState('');
  const load = () => { api.get('/playlists').then(r => setLists(r.data)); api.get('/tracks').then(r => setTracks(r.data)); };
  useEffect(() => { load(); }, []);

  const create = async e => {
    e.preventDefault(); setError('');
    if (!name.trim()) return;
    try { await api.post('/playlists', {name}); setName(''); load(); }
    catch (err) { setError(err.response?.data?.detail || 'Не удалось создать плейлист'); }
  };
  const removePlaylist = async p => {
    if (!window.confirm(`Удалить плейлист «${p.name}»?`)) return;
    await api.delete(`/playlists/${p.id}`); load();
  };
  const removeTrack = async (p, t) => { await api.delete(`/playlists/${p.id}/tracks/${t.id}`); load(); };

  return (
    <section>
      <div className="title-row">
        <div><h1>Плейлисты</h1><p className="muted">Создавай собственные подборки</p></div>
        <form className="playlist-create" onSubmit={create}>
          <input value={name} onChange={e => setName(e.target.value)} placeholder="Название плейлиста" maxLength={100}/>
          <button className="btn btn-primary">Создать</button>
        </form>
      </div>
      {error && <div className="alert alert-danger py-2 mt-3">{error}</div>}
      {lists && !lists.length && <div className="empty mt-4">У вас пока нет плейлистов. Создайте первый выше, а добавлять треки можно кнопкой <i className="bi bi-plus-square"/> у любого трека.</div>}
      {(lists || []).map(p => (
        <div className="playlist-card" key={p.id}>
          <div className="playlist-head">
            <h3><i className="bi bi-music-note-list"/> {p.name} <small className="muted">{tracksWord(p.tracks.length)}</small></h3>
            <button className="icon-btn" title="Удалить плейлист" onClick={() => removePlaylist(p)}><i className="bi bi-trash"/></button>
          </div>
          {p.tracks.length === 0 && <div className="muted">Плейлист пуст</div>}
          <TrackList tracks={p.tracks} hideTools extra={t => <button className="icon-btn" title="Убрать из плейлиста" onClick={() => removeTrack(p, t)}><i className="bi bi-x-lg"/></button>}/>
          <details><summary>Добавить трек</summary><div className="add-track-list">
            {tracks.filter(t => !p.tracks.some(x => x.id === t.id)).map(t => <button key={t.id} onClick={async () => { await api.post(`/playlists/${p.id}/tracks/${t.id}`); load(); }}>+ {t.artist} — {t.title}</button>)}
          </div></details>
        </div>
      ))}
    </section>
  );
}
