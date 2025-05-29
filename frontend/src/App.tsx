import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import GamePage from './pages/GamePage'
import DownloadPage from './pages/DownloadPage.jsx'
import Navbar from './components/Navbar'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-400 to-sky-600">
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/play" element={<GamePage />} />
        <Route path="/download" element={<DownloadPage />} />
      </Routes>
    </div>
  )
}

export default App 