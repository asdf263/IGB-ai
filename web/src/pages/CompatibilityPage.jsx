import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Heart, Loader2, AlertCircle, Sparkles } from 'lucide-react'
import useStore from '../store/useStore'
import { calculateCompatibility } from '../services/api'

function CompatibilityPage() {
  const navigate = useNavigate()
  const { currentMessages, userFeatures, compatibility, setCompatibility } = useStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedUser1, setSelectedUser1] = useState(null)
  const [selectedUser2, setSelectedUser2] = useState(null)

  const participants = userFeatures?.participants || []

  useEffect(() => {
    if (participants.length >= 2) {
      setSelectedUser1(participants[0])
      setSelectedUser2(participants[1])
    }
  }, [participants])

  const handleCalculate = async () => {
    if (!currentMessages || !selectedUser1 || !selectedUser2) return

    setLoading(true)
    setError(null)

    try {
      const result = await calculateCompatibility(currentMessages, selectedUser1, selectedUser2)
      if (result.success) {
        setCompatibility(result)
      } else {
        setError(result.error || 'Failed to calculate compatibility')
      }
    } catch (err) {
      setError(err.message || 'Failed to calculate compatibility')
    } finally {
      setLoading(false)
    }
  }

  if (!currentMessages || !userFeatures) {
    return (
      <div className="text-center py-20">
        <Heart className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h2 className="text-xl font-semibold text-gray-600 mb-2">No Conversation Data</h2>
        <p className="text-gray-500 mb-6">Upload a chat log to analyze compatibility</p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Upload Chat Log
        </button>
      </div>
    )
  }

  const getScoreColor = (score) => {
    if (score >= 75) return 'text-green-600'
    if (score >= 50) return 'text-yellow-600'
    return 'text-red-500'
  }

  const getScoreBg = (score) => {
    if (score >= 75) return 'bg-green-500'
    if (score >= 50) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center mb-4">
          <Heart className="w-6 h-6 text-pink-500 mr-2" />
          <h2 className="text-2xl font-bold text-gray-900">Compatibility Analysis</h2>
        </div>
        <p className="text-gray-600 mb-6">
          Analyze communication compatibility between conversation participants using AI
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">First Person</label>
            <select
              value={selectedUser1 || ''}
              onChange={(e) => setSelectedUser1(e.target.value)}
              className="input"
            >
              <option value="">Select user...</option>
              {participants.map((user) => (
                <option key={user} value={user}>{user}</option>
              ))}
            </select>
          </div>

          <div className="flex justify-center">
            <Heart className="w-8 h-8 text-pink-400" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Second Person</label>
            <select
              value={selectedUser2 || ''}
              onChange={(e) => setSelectedUser2(e.target.value)}
              className="input"
            >
              <option value="">Select user...</option>
              {participants.map((user) => (
                <option key={user} value={user}>{user}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleCalculate}
          disabled={loading || !selectedUser1 || !selectedUser2 || selectedUser1 === selectedUser2}
          className="btn-primary w-full mt-6 flex items-center justify-center disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Analyzing Compatibility...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5 mr-2" />
              Calculate Compatibility
            </>
          )}
        </button>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
            <AlertCircle className="w-5 h-5 mr-2" />
            {error}
          </div>
        )}
      </div>

      {compatibility && (
        <div className="card bg-gradient-to-br from-pink-50 via-purple-50 to-indigo-50 border-pink-200">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-white shadow-lg mb-4">
              <span className={`text-5xl font-bold ${getScoreColor(compatibility.compatibility?.overall_score || 0)}`}>
                {compatibility.compatibility?.overall_score || 0}%
              </span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">
              {compatibility.compatibility?.user1} & {compatibility.compatibility?.user2}
            </h3>
            <p className="text-gray-600 mt-2 max-w-xl mx-auto italic">
              "{compatibility.compatibility?.summary}"
            </p>
            <div className="mt-2 text-xs text-gray-400">
              Analysis: {compatibility.compatibility?.method === 'gemini' ? 'AI-Powered (Gemini)' : 'Algorithmic'}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h4 className="text-sm font-medium text-gray-500 mb-2">Communication Style</h4>
              <div className="flex items-end justify-between">
                <span className={`text-3xl font-bold ${getScoreColor(compatibility.compatibility?.communication_style_match || 0)}`}>
                  {compatibility.compatibility?.communication_style_match || 0}%
                </span>
                <div className="w-24 h-2 bg-gray-200 rounded-full">
                  <div
                    className={`h-full rounded-full ${getScoreBg(compatibility.compatibility?.communication_style_match || 0)}`}
                    style={{ width: `${compatibility.compatibility?.communication_style_match || 0}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h4 className="text-sm font-medium text-gray-500 mb-2">Emotional Compatibility</h4>
              <div className="flex items-end justify-between">
                <span className={`text-3xl font-bold ${getScoreColor(compatibility.compatibility?.emotional_compatibility || 0)}`}>
                  {compatibility.compatibility?.emotional_compatibility || 0}%
                </span>
                <div className="w-24 h-2 bg-gray-200 rounded-full">
                  <div
                    className={`h-full rounded-full ${getScoreBg(compatibility.compatibility?.emotional_compatibility || 0)}`}
                    style={{ width: `${compatibility.compatibility?.emotional_compatibility || 0}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h4 className="text-sm font-medium text-gray-500 mb-2">Engagement Balance</h4>
              <div className="flex items-end justify-between">
                <span className={`text-3xl font-bold ${getScoreColor(compatibility.compatibility?.engagement_balance || 0)}`}>
                  {compatibility.compatibility?.engagement_balance || 0}%
                </span>
                <div className="w-24 h-2 bg-gray-200 rounded-full">
                  <div
                    className={`h-full rounded-full ${getScoreBg(compatibility.compatibility?.engagement_balance || 0)}`}
                    style={{ width: `${compatibility.compatibility?.engagement_balance || 0}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h4 className="font-semibold text-green-700 mb-3">Strengths</h4>
              <ul className="space-y-2">
                {compatibility.compatibility?.strengths?.map((s, i) => (
                  <li key={i} className="flex items-start text-gray-700">
                    <span className="text-green-500 mr-2">✓</span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h4 className="font-semibold text-amber-700 mb-3">Areas for Growth</h4>
              <ul className="space-y-2">
                {compatibility.compatibility?.challenges?.map((c, i) => (
                  <li key={i} className="flex items-start text-gray-700">
                    <span className="text-amber-500 mr-2">!</span>
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {compatibility.compatibility?.recommendations && (
            <div className="mt-6 bg-white rounded-xl p-6 shadow-sm">
              <h4 className="font-semibold text-blue-700 mb-3">Recommendations</h4>
              <ul className="space-y-2">
                {compatibility.compatibility.recommendations.map((r, i) => (
                  <li key={i} className="flex items-start text-gray-700">
                    <span className="text-blue-500 mr-2">→</span>
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default CompatibilityPage
