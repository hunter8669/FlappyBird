import { Link, useLocation } from 'react-router-dom'
import { Home, Play, Download } from 'lucide-react'

const Navbar = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', icon: Home, label: '首页' },
    { path: '/play', icon: Play, label: '在线游戏' },
    { path: '/download', icon: Download, label: '下载游戏' }
  ]

  return (
    <nav className="bg-yellow-400 shadow-lg">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-2">
            <div className="text-2xl">🐦</div>
            <span className="pixel-font text-lg text-gray-800">FlapPy Bird</span>
          </Link>
          
          <div className="flex space-x-6">
            {navItems.map(({ path, icon: Icon, label }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  location.pathname === path
                    ? 'bg-orange-500 text-white'
                    : 'text-gray-800 hover:bg-orange-300'
                }`}
              >
                <Icon size={18} />
                <span className="text-sm">{label}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar 