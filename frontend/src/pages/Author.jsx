import {useEffect, useState} from "react";
import {Link, useSearchParams} from "react-router-dom";
import api from "../api/api";
import TrackList from "../components/TrackList";
import TagChips from "../components/TagChips";
import useFavorites from "../hooks/useFavorites";
import {tracksWord} from "../utils";

export default function Author() {
  const [params] = useSearchParams();
  const name = params.get("name") || "";
  const [author, setAuthor] = useState(null);
  const [error, setError] = useState("");
  const fav = useFavorites();

  useEffect(() => {
    setAuthor(null); setError("");
    api.get("/authors/detail", {params: {name}})
      .then(r => setAuthor(r.data))
      .catch(err => setError(err.response?.data?.detail || "Не удалось загрузить автора"));
  }, [name]);

  return (
    <section>
      <Link className="back-link" to="/authors"><i className="bi bi-chevron-left"/> Все авторы</Link>
      {error && <div className="empty mt-3">{error}</div>}
      {author && <>
        <div className="author-head">
          <div className="author-avatar big">{author.name.charAt(0).toUpperCase()}</div>
          <div>
            <span className="eyebrow">АВТОР</span>
            <h1>{author.name}</h1>
            <p className="muted mb-2">{tracksWord(author.tracks_count)}</p>
            <TagChips tags={author.top_tags}/>
          </div>
        </div>
        <TrackList tracks={author.tracks} onFavorite={fav.toggle} favoriteIds={fav.ids}/>
      </>}
    </section>
  );
}
