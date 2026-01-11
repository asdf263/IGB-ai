import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { History, Trash2, Eye, Loader2, AlertCircle, Users, Calendar } from 'lucide-react'
import useStore from '../store/useStore'
import { listAnalyses, getAnalysis, deleteAnalysis } from '../services/api'

function HistoryPage() {
  const navigate = useNavigate()
  const { setCurrentVector, setFeatureLabels, setCategories, setUserFeatures, setCurrentMessages, setCompatibility } = useStore()
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [loadingId, setLoadingId] = useState(null)

  useEffect(() => {
    loadAnalyses()
  }, [])

  const loadAnalyses = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await listAnalyses(50, 0)
      if (result.success) {
        setAnalyses(result.analyses)
      }
    } catch (err) {
      setError(err.message || 'Failed to load analyses')
    } finally {
      setLoading(false)
    }
  }

  const handleView = async (analysisId) => {
    setLoadingId(analysisId)
    try {
      const result = await getAnalysis(analysisId)
      if (result.success && result.analysis) {
        const analysis = result.analysis

        // Load conversation features
        if (analysis.conversation_features) {
          setCurrentVector(analysis.conversation_features.vector)
          setFeatureLabels(analysis.conversation_features.labels)
          setCategories(analysis.conversation_features.categories)
        }

        // Load user features
        if (analysis.user_features) {
          setUserFeatures({
            success: true,
            participants: analysis.participants,
            users: analysis.user_features,
            total_messages: analysis.message_count,
          })
        }

        // Load messages
        if (analysis.messages) {
          setCurrentMessages(analysis.messages)
        }

        // Load compatibility if available
        if (analysis.compatibility) {
          setCompatibility({ compatibility: analysis.compatibility })
        }

        navigate('/analysis')
      }
    } catch (err) {
      setError(err.message || 'Failed to load analysis')
    } finally {
      setLoadingId(null)
    }
  }

  const handleDelete = async (analysisId) => {
    if (!window.confirm('Are you sure you want to delete this analysis?')) {
      return
    }

    try {
      await deleteAnalysis(analysisId)
      setAnalyses(analyses.filter((a) => a.analysis_id !== analysisId))
    } catch (err) {
      setError(err.message || 'Failed to delete analysis')
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="text-center py-20">
        <Loader2 className="w-12 h-12 mx-auto text-sky-500 animate-spin mb-4" />
        <p className="text-gray-600">Loading past analyses...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <History className="w-6 h-6 text-sky-500 mr-2" />
            <h2 className="text-2xl font-bold text-gray-900">Analysis History</h2>
          </div>
          <button onClick={loadAnalyses} className="btn-secondary text-sm">
            Refresh
          </button>
        </div>
        <p className="text-gray-600">
          View and restore past conversation analyses. Each upload creates a new analysis file.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
          <AlertCircle className="w-5 h-5 mr-2" />
          {error}
        </div>
      )}

      {analyses.length === 0 ? (
        <div className="card text-center py-12">
          <History className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">No Analyses Yet</h3>
          <p className="text-gray-500 mb-6">Upload a chat log to create your first analysis</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Upload Chat Log
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {analyses.map((analysis) => (
            <div
              key={analysis.analysis_id}
              className="card hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <span className="font-mono text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      {analysis.analysis_id}
                    </span>
                    {analysis.has_compatibility && (
                      <span className="ml-2 text-xs bg-pink-100 text-pink-700 px-2 py-1 rounded">
                        Has Compatibility
                      </span>
                    )}
                  </div>

                  <div className="flex items-center text-sm text-gray-600 space-x-4">
                    <div className="flex items-center">
                      <Users className="w-4 h-4 mr-1" />
                      {analysis.participants?.join(', ') || 'Unknown'}
                    </div>
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      {formatDate(analysis.created_at)}
                    </div>
                    <div>
                      {analysis.message_count} messages
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleView(analysis.analysis_id)}
                    disabled={loadingId === analysis.analysis_id}
                    className="btn-primary text-sm flex items-center"
                  >
                    {loadingId === analysis.analysis_id ? (
                      <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    ) : (
                      <Eye className="w-4 h-4 mr-1" />
                    )}
                    View
                  </button>
                  <button
                    onClick={() => handleDelete(analysis.analysis_id)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete analysis"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default HistoryPage
