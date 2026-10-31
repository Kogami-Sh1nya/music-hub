import {useState} from "react";
import api from "../api/api";

export default function TagEditor({track, onSaved, onClose}) {
  const [value, setValue] = useState(track.tags.map(t => t.name).join(", "));
  const [error, setError] = useState("");
  const save = async e => {
    e.preventDefault(); setError("");
    try {
      const r = await api.put(`/tracks/${track.id}/tags`, {tags: value.split(",")});
      onSaved(r.data.tags);
    } catch (err) { setError(err.response?.data?.detail || "Не удалось сохранить теги"); }
  };
  return (
    <form className="tag-editor" onSubmit={save}>
      <input autoFocus value={value} onChange={e => setValue(e.target.value)} placeholder="Теги через запятую: рок, грустное, для спорта" maxLength={300}/>
      <button className="btn btn-primary btn-sm">Сохранить</button>
      <button type="button" className="btn btn-outline-secondary btn-sm" onClick={onClose}>Отмена</button>
      {error && <span className="tag-editor-error">{error}</span>}
    </form>
  );
}
