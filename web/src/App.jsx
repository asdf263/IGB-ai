import React from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import { Upload, BarChart3, Network, Sparkles } from 'lucide-react'
import UploadPage from './pages/UploadPage'
import AnalysisPage from './pages/AnalysisPage'
import ClusterPage from './pages/ClusterPage'
import SyntheticPage from './pages/SyntheticPage'

const navItems = [
  { path: '/', label: 'Upload', icon: Upload },
  { path: '/analysis', label: 'Analysis', icon: BarChart3 },
  { path: '/clusters', label: 'Clusters', icon: Network },
  { path: '/synthetic', label: 'Synthetic', icon: Sparkles },
]

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold text-primary-600">IGB AI</span>
              <span className="ml-2 text-sm text-gray-500">Behavior Vectors</span>
            </div>
            <div className="flex space-x-1">
              {navItems.map(({ path, label, icon: Icon }) => (
                <NavLink
                  key={path}
                  to={path}
                  className={({ isActive }) =>
                    `flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100'
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
          <Route path="/clusters" element={<ClusterPage />} />
          <Route path="/synthetic" element={<SyntheticPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
