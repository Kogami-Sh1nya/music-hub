import {useCallback, useEffect, useState} from "react";
import api from "../api/api";

export default function useFavorites() {
  const [ids, setIds] = useState([]);
  const load = useCallback(() => api.get("/favorites").then(r => setIds(r.data.map(x => x.id))).catch(() => {}), []);
  useEffect(() => { load(); }, [load]);
  const toggle = async t => {
    if (ids.includes(t.id)) await api.delete(`/favorites/${t.id}`);
    else await api.post(`/favorites/${t.id}`);
    load();
  };
  return {ids, toggle};
}
