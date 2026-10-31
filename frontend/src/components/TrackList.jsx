import {useState} from "react";
import {Link} from "react-router-dom";
import {usePlayer} from "../context/PlayerContext";
import {authorLink} from "../utils";
import TagChips from "./TagChips";
import TagEditor from "./TagEditor";
import AddToPlaylist from "./AddToPlaylist";

// hideTools — скрыть кнопки «теги» и «в плейлист» (например, внутри самого плейлиста)
export default function TrackList({tracks, onFavorite, favoriteIds = [], extra, hideTools = false}) {
  const {play, track, playing} = usePlayer();
  const [editing, setEditing] = useState(null);
  const [tagsById, setTagsById] = useState({});

  return (
    <div className="track-list">
      {tracks.map((t, i) => {
        const tags = tagsById[t.id] ?? t.tags ?? [];
        return (
          <div className="track-item" key={t.id}>
            <div className={`track-row ${track?.id === t.id ? "current" : ""}`}>
              <button className="play-mini" onClick={() => play(t)}><i className={`bi ${track?.id === t.id && playing ? "bi-volume-up-fill" : "bi-play-fill"}`}/></button>
              <div className="track-number">{i + 1}</div>
              <div className="track-info">
                <strong>{t.title}</strong>
                <span><Link className="artist-link" to={authorLink(t.artist)}>{t.artist}</Link></span>
                <TagChips tags={tags}/>
              </div>
              <div className="album">{t.album}</div>
              <div className="track-actions">
                {!hideTools && <button className="icon-btn" title="Теги" onClick={() => setEditing(editing === t.id ? null : t.id)}><i className="bi bi-tags"/></button>}
                {!hideTools && <AddToPlaylist track={t}/>}
                {onFavorite && <button className="icon-btn" onClick={() => onFavorite(t)}><i className={`bi ${favoriteIds.includes(t.id) ? "bi-heart-fill" : "bi-heart"}`}/></button>}
                {extra && extra(t)}
              </div>
            </div>
            {editing === t.id && (
              <TagEditor track={{...t, tags}} onClose={() => setEditing(null)}
                onSaved={newTags => { setTagsById({...tagsById, [t.id]: newTags}); setEditing(null); }}/>
            )}
          </div>
        );
      })}
    </div>
  );
}
