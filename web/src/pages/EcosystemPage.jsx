import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Globe,
  Users,
  Trash2,
  MessageCircle,
  Heart,
  Loader2,
  AlertCircle,
  Plus,
  Sparkles,
} from 'lucide-react'
import {
  listEcosystemPersonas,
  removePersonaFromEcosystem,
  computeEcosystemCompatibility,
  findBestMatches,
  listAnalyses,
  createPersonasFromAnalysis,
} from '../services/api'

function EcosystemPage() {
  const navigate = useNavigate()
  const [personas, setPersonas] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedPersona1, setSelectedPersona1] = useState(null)
  const [selectedPersona2, setSelectedPersona2] = useState(null)
  const [compatibility, setCompatibility] = useState(null)
  const [computingCompat, setComputingCompat] = useState(false)
  const [matches, setMatches] = useState(null)
  const [loadingMatches, setLoadingMatches] = useState(false)
  const [analyses, setAnalyses] = useState([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [addingFromAnalysis, setAddingFromAnalysis] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [personasResult, analysesResult] = await Promise.all([
        listEcosystemPersonas(),
        listAnalyses(20, 0),
      ])

      if (personasResult.success) {
        setPersonas(personasResult.personas)
        setStats(personasResult.stats)
      }
      if (analysesResult.success) {
        setAnalyses(analysesResult.analyses)
      }
    } catch (err) {
      setError(err.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleRemovePersona = async (personaId) => {
    if (!window.confirm('Remove this persona from the ecosystem?')) return

    try {
      await removePersonaFromEcosystem(personaId)
      setPersonas(personas.filter((p) => p.persona_id !== personaId))
      if (selectedPersona1?.persona_id === personaId) setSelectedPersona1(null)
      if (selectedPersona2?.persona_id === personaId) setSelectedPersona2(null)
    } catch (err) {
      setError('Failed to remove persona')
    }
  }

  const handleComputeCompatibility = async () => {
    if (!selectedPersona1 || !selectedPersona2) return

    setComputingCompat(true)
    setCompatibility(null)
    try {
      const result = await computeEcosystemCompatibility(
        selectedPersona1.persona_id,
        selectedPersona2.persona_id
      )
      if (result.success) {
        setCompatibility(result.compatibility)
      }
    } catch (err) {
      setError('Failed to compute compatibility')
    } finally {
      setComputingCompat(false)
    }
  }

  const handleFindMatches = async (personaId) => {
    setLoadingMatches(true)
    setMatches(null)
    try {
      const result = await findBestMatches(personaId, 5)
      if (result.success) {
        setMatches({ personaId, matches: result.matches })
      }
    } catch (err) {
      setError('Failed to find matches')
    } finally {
      setLoadingMatches(false)
    }
  }

  const handleAddFromAnalysis = async (analysisId) => {
    setAddingFromAnalysis(analysisId)
    try {
      const result = await createPersonasFromAnalysis(analysisId)
      if (result.success) {
        setShowAddModal(false)
        await loadData()
      }
    } catch (err) {
      setError('Failed to create personas from analysis')
    } finally {
      setAddingFromAnalysis(null)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 75) return 'text-green-600'
    if (score >= 50) return 'text-yellow-600'
    return 'text-red-500'
  }

  if (loading) {
    return (
      <div className="text-center py-20">
        <Loader2 className="w-12 h-12 mx-auto text-sky-500 animate-spin mb-4" />
        <p className="text-gray-600">Loading ecosystem...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Globe className="w-6 h-6 text-purple-500 mr-2" />
            <h2 className="text-2xl font-bold text-gray-900">Personality Ecosystem</h2>
          </div>
          <button onClick={() => setShowAddModal(true)} className="btn-primary flex items-center">
            <Plus className="w-4 h-4 mr-2" />
            Add Personas
          </button>
        </div>
        <p className="text-gray-600">
          A shared environment where AI personalities interact. Compare behavioral vectors,
          compute compatibility, and explore interpersonal dynamics.
        </p>

        {stats && (
          <div className="grid grid-cols-4 gap-4 mt-4">
            <div className="bg-purple-50 p-3 rounded-lg text-center">
              <div className="text-2xl font-bold text-purple-600">{stats.total_personas}</div>
              <div className="text-xs text-gray-600">Personas</div>
            </div>
            <div className="bg-sky-50 p-3 rounded-lg text-center">
              <div className="text-2xl font-bold text-sky-600">
                {(stats.avg_extraversion * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-600">Avg Extraversion</div>
            </div>
            <div className="bg-green-50 p-3 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">
                {(stats.avg_agreeableness * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-600">Avg Agreeableness</div>
            </div>
            <div className="bg-orange-50 p-3 rounded-lg text-center">
              <div className="text-2xl font-bold text-orange-600">{stats.total_interactions}</div>
              <div className="text-xs text-gray-600">Total Chats</div>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
          <AlertCircle className="w-5 h-5 mr-2" />
          {error}
          <button onClick={() => setError(null)} className="ml-auto text-red-500 hover:text-red-700">
            ×
          </button>
        </div>
      )}

      {personas.length === 0 ? (
        <div className="card text-center py-12">
          <Users className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">No Personas Yet</h3>
          <p className="text-gray-500 mb-6">
            Add personas from your analyses to populate the ecosystem
          </p>
          <button onClick={() => setShowAddModal(true)} className="btn-primary">
            Add Personas
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Personas List */}
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
              <Users className="w-5 h-5 mr-2 text-purple-500" />
              Personas ({personas.length})
            </h3>
            <div className="space-y-3">
              {personas.map((persona) => (
                <div
                  key={persona.persona_id}
                  className={`p-4 rounded-lg border-2 transition-colors ${
                    selectedPersona1?.persona_id === persona.persona_id
                      ? 'border-sky-400 bg-sky-50'
                      : selectedPersona2?.persona_id === persona.persona_id
                      ? 'border-purple-400 bg-purple-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{persona.user_name}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {persona.interaction_count || 0} interactions
                        {persona.metrics?.extraversion && (
                          <span className="ml-2">
                            • E: {(persona.metrics.extraversion * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          if (!selectedPersona1) setSelectedPersona1(persona)
                          else if (!selectedPersona2 && selectedPersona1.persona_id !== persona.persona_id)
                            setSelectedPersona2(persona)
                          else if (selectedPersona1.persona_id === persona.persona_id)
                            setSelectedPersona1(null)
                          else setSelectedPersona2(null)
                        }}
                        className={`px-3 py-1 text-sm rounded ${
                          selectedPersona1?.persona_id === persona.persona_id
                            ? 'bg-sky-500 text-white'
                            : selectedPersona2?.persona_id === persona.persona_id
                            ? 'bg-purple-500 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        {selectedPersona1?.persona_id === persona.persona_id
                          ? 'Person 1'
                          : selectedPersona2?.persona_id === persona.persona_id
                          ? 'Person 2'
                          : 'Select'}
                      </button>
                      <button
                        onClick={() => navigate('/chat')}
                        className="p-2 text-sky-500 hover:bg-sky-50 rounded"
                        title="Chat with persona"
                      >
                        <MessageCircle className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleFindMatches(persona.persona_id)}
                        className="p-2 text-pink-500 hover:bg-pink-50 rounded"
                        title="Find matches"
                      >
                        <Heart className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleRemovePersona(persona.persona_id)}
                        className="p-2 text-red-500 hover:bg-red-50 rounded"
                        title="Remove persona"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {selectedPersona1 && selectedPersona2 && (
              <button
                onClick={handleComputeCompatibility}
                disabled={computingCompat}
                className="btn-primary w-full mt-4 flex items-center justify-center"
              >
                {computingCompat ? (
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                ) : (
                  <Sparkles className="w-5 h-5 mr-2" />
                )}
                Compute Compatibility
              </button>
            )}
          </div>

          {/* Compatibility Results */}
          <div className="space-y-4">
            {compatibility && (
              <div className="card bg-gradient-to-br from-pink-50 to-purple-50 border-pink-200">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                  <Heart className="w-5 h-5 mr-2 text-pink-500" />
                  Compatibility: {compatibility.persona1} & {compatibility.persona2}
                </h3>

                <div className="text-center mb-6">
                  <div
                    className={`text-5xl font-bold ${getScoreColor(compatibility.overall_score)}`}
                  >
                    {compatibility.overall_score}%
                  </div>
                  <div className="text-gray-600 mt-1">Overall Compatibility</div>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-4">
                  {Object.entries(compatibility.dimension_scores || {}).map(([dim, score]) => (
                    <div key={dim} className="bg-white p-3 rounded-lg">
                      <div className="text-xs text-gray-500 capitalize">
                        {dim.replace(/_/g, ' ')}
                      </div>
                      <div className={`text-lg font-semibold ${getScoreColor(score)}`}>
                        {score}%
                      </div>
                    </div>
                  ))}
                </div>

                {compatibility.insights && (
                  <div className="bg-white p-4 rounded-lg mb-4">
                    <h4 className="font-medium text-gray-700 mb-2">Insights</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {compatibility.insights.map((insight, i) => (
                        <li key={i}>• {insight}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-green-50 p-3 rounded-lg">
                    <h4 className="font-medium text-green-700 mb-2">Strengths</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {compatibility.strengths?.map((s, i) => (
                        <li key={i}>✓ {s}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-amber-50 p-3 rounded-lg">
                    <h4 className="font-medium text-amber-700 mb-2">Challenges</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {compatibility.challenges?.map((c, i) => (
                        <li key={i}>! {c}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {matches && (
              <div className="card">
                <h3 className="font-semibold text-gray-900 mb-4">
                  Best Matches for{' '}
                  {personas.find((p) => p.persona_id === matches.personaId)?.user_name}
                </h3>
                {loadingMatches ? (
                  <div className="text-center py-4">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto text-gray-400" />
                  </div>
                ) : matches.matches.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">
                    No other personas to match with
                  </p>
                ) : (
                  <div className="space-y-2">
                    {matches.matches.map((match, i) => (
                      <div
                        key={match.persona_id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center">
                          <span className="w-6 h-6 rounded-full bg-pink-100 text-pink-600 flex items-center justify-center text-sm font-medium mr-3">
                            {i + 1}
                          </span>
                          <div>
                            <div className="font-medium">{match.user_name}</div>
                            {match.top_strength && (
                              <div className="text-xs text-gray-500">{match.top_strength}</div>
                            )}
                          </div>
                        </div>
                        <div className={`font-bold ${getScoreColor(match.overall_score)}`}>
                          {match.overall_score}%
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Add Personas Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Personas from Analysis</h3>
            <p className="text-gray-600 text-sm mb-4">
              Select an analysis to create AI personas for all participants.
            </p>

            {analyses.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                No analyses available. Upload a chat log first.
              </p>
            ) : (
              <div className="space-y-2">
                {analyses.map((analysis) => (
                  <button
                    key={analysis.analysis_id}
                    onClick={() => handleAddFromAnalysis(analysis.analysis_id)}
                    disabled={addingFromAnalysis === analysis.analysis_id}
                    className="w-full p-3 text-left bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-gray-900">
                          {analysis.participants?.join(' & ') || 'Unknown'}
                        </div>
                        <div className="text-xs text-gray-500">
                          {analysis.message_count} messages
                        </div>
                      </div>
                      {addingFromAnalysis === analysis.analysis_id ? (
                        <Loader2 className="w-5 h-5 animate-spin text-sky-500" />
                      ) : (
                        <Plus className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}

            <button
              onClick={() => setShowAddModal(false)}
              className="w-full mt-4 py-2 text-gray-600 hover:text-gray-900"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default EcosystemPage
