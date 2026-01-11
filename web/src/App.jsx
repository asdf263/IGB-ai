import React from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import { Upload, BarChart3, Network, Sparkles, User, Heart, History, MessageCircle, Globe } from 'lucide-react'
import UploadPage from './pages/UploadPage'
import AnalysisPage from './pages/AnalysisPage'
import ClusterPage from './pages/ClusterPage'
import SyntheticPage from './pages/SyntheticPage'
import UserProfilePage from './pages/UserProfilePage'
import CompatibilityPage from './pages/CompatibilityPage'
import HistoryPage from './pages/HistoryPage'
import ChatPage from './pages/ChatPage'
import EcosystemPage from './pages/EcosystemPage'

const navItems = [
  { path: '/', label: 'Upload', icon: Upload },
  { path: '/analysis', label: 'Analysis', icon: BarChart3 },
  { path: '/users', label: 'Users', icon: User },
  { path: '/compatibility', label: 'Compatibility', icon: Heart },
  { path: '/ecosystem', label: 'Ecosystem', icon: Globe },
  { path: '/chat', label: 'Chat', icon: MessageCircle },
  { path: '/history', label: 'History', icon: History },
]

function App() {
  return (
    <div className="min-h-screen bg-rose-50">
      <nav className="bg-white shadow-sm border-b border-rose-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold text-rose-600">IGB AI</span>
              <span className="ml-2 text-sm text-rose-400">Matchmaking Intelligence</span>
            </div>
            <div className="flex space-x-1">
              {navItems.map(({ path, label, icon: Icon }) => (
                <NavLink
                  key={path}
                  to={path}
                  className={({ isActive }) =>
                    `flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      isActive
                        ? 'bg-rose-100 text-rose-700'
                        : 'text-rose-600 hover:bg-rose-50'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {label}
                </NavLink>
              ))}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/users" element={<UserProfilePage />} />
          <Route path="/compatibility" element={<CompatibilityPage />} />
          <Route path="/ecosystem" element={<EcosystemPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/clusters" element={<ClusterPage />} />
          <Route path="/synthetic" element={<SyntheticPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
