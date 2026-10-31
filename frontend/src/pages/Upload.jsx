import {useEffect, useState} from "react";
import api from "../api/api";

const GENRES = ["рок", "поп", "хип-хоп", "электроника", "джаз", "классика", "метал", "инди", "r&b", "блюз", "фолк", "lo-fi"];
const EMPTY = {title: '', artist: '', album: '', tags: ''};

export default function Upload() {
  const [form, setForm] = useState(EMPTY), [file, setFile] = useState(), [msg, setMsg] = useState(''), [popular, setPopular] = useState([]);
  useEffect(() => { api.get('/tags').then(r => setPopular(r.data.map(t => t.name))).catch(() => {}); }, []);
  const suggestions = [...new Set([...popular, ...GENRES])].slice(0, 16);
  const current = form.tags.split(',').map(x => x.trim().toLowerCase()).filter(Boolean);

  const addTag = tag => {
    if (current.includes(tag)) return;
    setForm({...form, tags: [...form.tags.split(',').map(x => x.trim()).filter(Boolean), tag].join(', ')});
  };
  const submit = async e => {
    e.preventDefault();
    const d = new FormData();
    Object.entries(form).forEach(([k, v]) => d.append(k, v));
    d.append('file', file);
    try { await api.post('/tracks/upload', d); setMsg('Трек успешно загружен'); setForm(EMPTY); setFile(null); }
    catch (err) { setMsg(err.response?.data?.detail || 'Ошибка загрузки'); }
  };

  return <section><h1>Загрузка музыки</h1><div className="upload-card"><form onSubmit={submit}>
    <label>Название</label><input className="form-control" required value={form.title} onChange={e => setForm({...form, title: e.target.value})}/>
    <label>Исполнитель</label><input className="form-control" required value={form.artist} onChange={e => setForm({...form, artist: e.target.value})}/>
    <label>Альбом</label><input className="form-control" value={form.album} onChange={e => setForm({...form, album: e.target.value})}/>
    <label>Теги (через запятую)</label><input className="form-control" placeholder="рок, грустное, для спорта" value={form.tags} onChange={e => setForm({...form, tags: e.target.value})}/>
    <div className="tag-chips tag-suggest">{suggestions.map(t => <button type="button" key={t} className={`tag-chip ${current.includes(t) ? 'on' : ''}`} onClick={() => addTag(t)}>#{t}</button>)}</div>
    <label>Аудиофайл</label><input className="form-control" required type="file" accept="audio/*" onChange={e => setFile(e.target.files[0])}/>
    <button className="btn btn-primary mt-4">Загрузить трек</button>{msg && <p className="mt-3">{msg}</p>}
  </form></div></section>;
}
