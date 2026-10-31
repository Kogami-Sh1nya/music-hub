import {useState} from "react";
import {BrowserRouter, Routes, Route} from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Player from "./components/Player";
import Auth from "./pages/Auth";
import Home from "./pages/Home";
import Search from "./pages/Search";
import Favorites from "./pages/Favorites";
import Playlists from "./pages/Playlists";
import Upload from "./pages/Upload";
import Authors from "./pages/Authors";
import Author from "./pages/Author";
import Tags from "./pages/Tags";
import Profile from "./pages/Profile";
import {PlayerProvider} from "./context/PlayerContext";

export default function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem('token'));
  if (!authed) return <Auth onAuth={() => setAuthed(true)}/>;
  return (
    <BrowserRouter>
      <PlayerProvider>
        <div className="app-shell">
          <Sidebar logout={() => { localStorage.removeItem('token'); setAuthed(false); }}/>
          <main className="content">
            <Routes>
              <Route path="/" element={<Home/>}/>
              <Route path="/search" element={<Search/>}/>
              <Route path="/authors" element={<Authors/>}/>
              <Route path="/author" element={<Author/>}/>
              <Route path="/tags" element={<Tags/>}/>
              <Route path="/favorites" element={<Favorites/>}/>
              <Route path="/playlists" element={<Playlists/>}/>
              <Route path="/upload" element={<Upload/>}/>
              <Route path="/profile" element={<Profile/>}/>
            </Routes>
          </main>
          <Player/>
        </div>
      </PlayerProvider>
    </BrowserRouter>
  );
}
