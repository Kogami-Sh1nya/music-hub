import {createContext, useContext, useRef, useState} from "react";
import {API_URL} from "../api/api";
const PlayerContext = createContext();
export const usePlayer = () => useContext(PlayerContext);
export function PlayerProvider({children}) {
  const audioRef = useRef(null); const [track,setTrack]=useState(null); const [playing,setPlaying]=useState(false);
  const play = t => { setTrack(t); setTimeout(()=>audioRef.current?.play(),0); setPlaying(true); };
  const toggle = () => { if(!audioRef.current)return; playing?audioRef.current.pause():audioRef.current.play(); setPlaying(!playing); };
  return <PlayerContext.Provider value={{track,playing,play,toggle,audioRef,API_URL}}>{children}</PlayerContext.Provider>;
}
