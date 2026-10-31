import {useState} from "react";
import api from "../api/api";

export default function AddToPlaylist({track}) {
  const [open, setOpen] = useState(false);
  const [lists, setLists] = useState([]);
  const [name, setName] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const loadLists = () => api.get("/playlists").then(r => setLists(r.data)).catch(() => {});
  const toggle = () => {
    setMsg(""); setError("");
    if (!open) loadLists();
    setOpen(!open);
  };
  const add = async p => {
    setMsg(""); setError("");
    try {
      await api.post(`/playlists/${p.id}/tracks/${track.id}`);
      setMsg(`Добавлено в «${p.name}»`); loadLists();
    } catch (err) { setError(err.response?.data?.detail || "Ошибка"); }
  };
  const create = async e => {
    e.preventDefault(); setMsg(""); setError("");
    if (!name.trim()) return;
    try {
      const r = await api.post("/playlists", {name});
      await api.post(`/playlists/${r.data.id}/tracks/${track.id}`);
      setName(""); setMsg(`Создан «${r.data.name}», трек добавлен`); loadLists();
    } catch (err) { setError(err.response?.data?.detail || "Ошибка"); }
  };

  return (
    <div className="add-pl">
      <button className="icon-btn" title="Добавить в плейлист" onClick={toggle}><i className="bi bi-plus-square"/></button>
      {open && <>
        <div className="menu-backdrop" onClick={() => setOpen(false)}/>
        <div className="pl-menu">
          <div className="pl-title">Добавить в плейлист</div>
          {lists.length === 0 && <div className="pl-empty">Плейлистов пока нет — создайте первый ниже</div>}
          {lists.map(p => {
            const has = p.tracks.some(x => x.id === track.id);
            return (
              <button key={p.id} className="pl-item" disabled={has} onClick={() => add(p)}>
                <i className={`bi ${has ? "bi-check2" : "bi-music-note-list"}`}/> {p.name}
              </button>
            );
          })}
          <form className="pl-new" onSubmit={create}>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="Новый плейлист" maxLength={100}/>
            <button className="btn btn-primary btn-sm">+</button>
          </form>
          {msg && <div className="pl-msg">{msg}</div>}
          {error && <div className="pl-error">{error}</div>}
        </div>
      </>}
    </div>
  );
}
