import { useEffect, useState } from "react";
import api from "../api/api";
import TrackList from "../components/TrackList";

export default function Favorites() {
  const [tracks, setTracks] = useState([]);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const response = await api.get("/favorites");
      setTracks(response.data);
      setError("");
    } catch (err) {
      console.error("Ошибка загрузки избранного:", err);
      setError("Не удалось загрузить избранное");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const removeFavorite = async (track) => {
    try {
      await api.delete(`/favorites/${track.id}`);
      await load();
    } catch (err) {
      console.error("Ошибка удаления из избранного:", err);
      setError("Не удалось удалить трек из избранного");
    }
  };

  return (
    <section>
      <h1>Избранное</h1>
      <p className="muted">
        Треки, которые тебе понравились
      </p>

      {error && <p className="error">{error}</p>}

      <TrackList
        tracks={tracks}
        favoriteIds={tracks.map(t => t.id)}
        onFavorite={removeFavorite}
      />
    </section>
  );
}