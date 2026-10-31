import {useEffect, useState} from "react";
import {Link} from "react-router-dom";
import api from "../api/api";
import {authorLink, tracksWord} from "../utils";

export default function Authors() {
  const [authors, setAuthors] = useState(null);
  const [q, setQ] = useState("");
  useEffect(() => { api.get("/authors").then(r => setAuthors(r.data)); }, []);
  const shown = (authors || []).filter(a => a.name.toLowerCase().includes(q.trim().toLowerCase()));

  return (
    <section>
      <h1>Авторы</h1>
      <p className="muted">Все исполнители вашей библиотеки</p>
      <div className="searchbar"><i className="bi bi-search"/><input value={q} onChange={e => setQ(e.target.value)} placeholder="Найти автора..."/></div>
      {authors && !authors.length && <div className="empty">Авторов пока нет. Загрузите первый трек.</div>}
      {authors && authors.length > 0 && !shown.length && <div className="empty">Ничего не найдено</div>}
      <div className="authors-grid">
        {shown.map(a => (
          <Link key={a.name} className="author-card" to={authorLink(a.name)}>
            <div className="author-avatar">{a.name.charAt(0).toUpperCase()}</div>
            <strong>{a.name}</strong>
            <span>{tracksWord(a.tracks_count)}</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
