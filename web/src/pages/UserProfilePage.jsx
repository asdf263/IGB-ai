import React, { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import Plot from 'react-plotly.js'
import { User, ChevronDown, ChevronRight, Users, Heart } from 'lucide-react'
import useStore from '../store/useStore'

const categoryColors = {
  temporal: '#FF6B6B',
  text: '#4ECDC4',
  linguistic: '#45B7D1',
  semantic: '#96CEB4',
  sentiment: '#FFEAA7',
  behavioral: '#DDA0DD',
  graph: '#98D8C8',
  composite: '#F7DC6F',
  reaction: '#FF9F43',
  emotion: '#E74C3C',
  context: '#9B59B6',
  synthetic: '#1ABC9C',
}

function UserProfilePage() {
  const navigate = useNavigate()
  const { userFeatures, compatibility } = useStore()
  const [selectedUser, setSelectedUser] = useState(null)
  const [expandedCategories, setExpandedCategories] = useState({})

  const toggleCategory = (cat) => {
    setExpandedCategories((prev) => ({ ...prev, [cat]: !prev[cat] }))
  }

  const users = useMemo(() => {
    if (!userFeatures?.users) return []
    return Object.keys(userFeatures.users)
  }, [userFeatures])

  const currentUserData = useMemo(() => {
    if (!selectedUser || !userFeatures?.users) return null
    return userFeatures.users[selectedUser]
  }, [selectedUser, userFeatures])

  const radarData = useMemo(() => {
    if (!currentUserData?.categories) return null

    const categoryMeans = Object.entries(currentUserData.categories).map(([cat, features]) => {
      const values = Object.values(features).filter((v) => typeof v === 'number' && !isNaN(v))
      return {
        category: cat,
        mean: values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0,
      }
    })

    return {
      data: [
        {
          type: 'scatterpolar',
          r: categoryMeans.map((c) => Math.min(1, Math.max(0, c.mean))),
          theta: categoryMeans.map((c) => c.category),
          fill: 'toself',
          fillcolor: 'rgba(255, 159, 67, 0.2)',
          line: { color: '#FF9F43' },
          name: 'Category Scores',
        },
      ],
      layout: {
        polar: {
          radialaxis: { visible: true, range: [0, 1] },
        },
        showlegend: false,
        margin: { t: 40, b: 40, l: 40, r: 40 },
        height: 350,
      },
    }
  }, [currentUserData])

  const reactionFeatures = useMemo(() => {
    if (!currentUserData?.categories?.reaction) return null
    return currentUserData.categories.reaction
  }, [currentUserData])

  if (!userFeatures) {
    return (
      <div className="text-center py-20">
        <User className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h2 className="text-xl font-semibold text-gray-600 mb-2">No User Data</h2>
        <p className="text-gray-500 mb-6">Upload a chat log to see user profiles</p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Upload Chat Log
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">User Profiles</h2>
        <p className="text-gray-600 mb-4">
          Analyze individual behavior patterns based on reactions to others
        </p>

        <div className="flex flex-wrap gap-2">
          {users.map((user) => (
            <button
              key={user}
              onClick={() => setSelectedUser(user)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center ${
                selectedUser === user
                  ? 'bg-orange-100 text-orange-700 border-2 border-orange-300'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border-2 border-transparent'
              }`}
            >
              <User className="w-4 h-4 mr-2" />
              {user}
              <span className="ml-2 text-xs bg-gray-200 px-2 py-0.5 rounded-full">
                {userFeatures.users[user]?.message_count || 0} msgs
              </span>
            </button>
          ))}
        </div>
      </div>

      {selectedUser && currentUserData && (
        <>
          {/* Text Style Summary - Key visible features */}
          <div className="card bg-gradient-to-r from-teal-50 to-cyan-50 border-teal-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              ✍️ {selectedUser}'s Text Style
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {/* CAPS Usage */}
              <div className="bg-white p-4 rounded-lg border border-teal-200">
                <div className="text-xs text-gray-500 uppercase tracking-wide">CAPS Usage</div>
                <div className="text-2xl font-bold text-teal-600">
                  {((currentUserData.categories?.text?.uppercase_ratio || 0) * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-gray-500">
                  {(currentUserData.categories?.text?.all_caps_word_ratio || 0) > 0.1 
                    ? 'Uses ALL CAPS words' 
                    : 'Standard caps'}
                </div>
              </div>
              
              {/* Punctuation */}
              <div className="bg-white p-4 rounded-lg border border-teal-200">
                <div className="text-xs text-gray-500 uppercase tracking-wide">Punctuation</div>
                <div className="text-2xl font-bold text-teal-600">
                  {((currentUserData.categories?.text?.punctuation_ratio || 0) * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-gray-500">
                  {(currentUserData.categories?.linguistic?.exclamation_ratio || 0) > 0.2 
                    ? 'Uses !!! often' 
                    : 'Standard punctuation'}
                </div>
              </div>
              
              {/* Emoji */}
              <div className="bg-white p-4 rounded-lg border border-teal-200">
                <div className="text-xs text-gray-500 uppercase tracking-wide">Emoji Use</div>
                <div className="text-2xl font-bold text-teal-600">
                  {((currentUserData.categories?.text?.emoji_density || 0) * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500">
                  {(currentUserData.categories?.text?.emoji_density || 0) > 0.1 
                    ? 'Frequent emoji user' 
                    : 'Minimal emojis'}
                </div>
              </div>
              
              {/* Message Length */}
              <div className="bg-white p-4 rounded-lg border border-teal-200">
                <div className="text-xs text-gray-500 uppercase tracking-wide">Avg Words/Msg</div>
                <div className="text-2xl font-bold text-teal-600">
                  {((currentUserData.categories?.text?.word_count_mean || 0) * 50).toFixed(0)}
                </div>
                <div className="text-xs text-gray-500">
                  {(currentUserData.categories?.text?.word_count_mean || 0) < 0.2 
                    ? 'Short messages' 
                    : (currentUserData.categories?.text?.word_count_mean || 0) > 0.5 
                      ? 'Long messages' 
                      : 'Medium length'}
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {selectedUser}'s Behavior Profile
              </h3>
              {radarData && (
                <Plot
                  data={radarData.data}
                  layout={radarData.layout}
                  config={{ responsive: true, displayModeBar: false }}
                  className="w-full"
                />
              )}
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Reaction Patterns
              </h3>
              {reactionFeatures ? (
                <div className="space-y-3">
                  {Object.entries(reactionFeatures).slice(0, 10).map(([name, value]) => (
                    <div key={name} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 capitalize">
                        {name.replace(/_/g, ' ')}
                      </span>
                      <div className="flex items-center">
                        <div className="w-32 h-2 bg-gray-200 rounded-full mr-2">
                          <div
                            className="h-full bg-orange-500 rounded-full"
                            style={{ width: `${Math.min(100, Math.abs(value) * 100)}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium w-12 text-right">
                          {(value * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No reaction data available</p>
              )}
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">All Features by Category</h3>
            <div className="space-y-2">
              {currentUserData.categories &&
                Object.entries(currentUserData.categories).map(([cat, features]) => {
                  const isExpanded = expandedCategories[cat]
                  const featureCount = Object.keys(features).length
                  const values = Object.values(features).filter(v => typeof v === 'number' && !isNaN(v))
                  const avgValue = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0

                  return (
                    <div key={cat} className="border border-gray-200 rounded-lg overflow-hidden">
                      <button
                        onClick={() => toggleCategory(cat)}
                        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-center">
                          <div
                            className="w-3 h-3 rounded-full mr-3"
                            style={{ backgroundColor: categoryColors[cat] || '#999' }}
                          />
                          <span className="font-medium capitalize">{cat}</span>
                          <span className="ml-2 text-sm text-gray-500">
                            {featureCount} features • avg: {avgValue.toFixed(3)}
                          </span>
                        </div>
                        {isExpanded ? (
                          <ChevronDown className="w-5 h-5 text-gray-400" />
                        ) : (
                          <ChevronRight className="w-5 h-5 text-gray-400" />
                        )}
                      </button>

                      {isExpanded && (
                        <div className="border-t border-gray-200 bg-gray-50 p-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            {Object.entries(features).map(([name, value]) => (
                              <div key={name} className="bg-white p-3 rounded border border-gray-200">
                                <div className="text-xs text-gray-500 capitalize">
                                  {name.replace(/_/g, ' ')}
                                </div>
                                <div className="text-lg font-semibold">
                                  {typeof value === 'number' ? value.toFixed(4) : value}
                                </div>
                                <div className="mt-1 h-1 bg-gray-200 rounded overflow-hidden">
                                  <div
                                    className="h-full rounded"
                                    style={{
                                      width: `${Math.min(Math.abs(value) * 100, 100)}%`,
                                      backgroundColor: categoryColors[cat] || '#999',
                                    }}
                                  />
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
            </div>
          </div>
        </>
      )}

      <div className="flex gap-4">
        <button
          onClick={() => navigate('/compatibility')}
          className="btn-primary flex items-center"
        >
          <Heart className="w-4 h-4 mr-2" />
          View Compatibility Analysis
        </button>
        <button
          onClick={() => navigate('/chat')}
          className="btn-secondary flex items-center"
        >
          <Users className="w-4 h-4 mr-2" />
          Chat as Persona
        </button>
      </div>
    </div>
  )
}

export default UserProfilePage
