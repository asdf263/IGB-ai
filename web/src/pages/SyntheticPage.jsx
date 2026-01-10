import React, { useState } from 'react'
import Plot from 'react-plotly.js'
import { Sparkles, Loader2, RefreshCw } from 'lucide-react'
import useStore from '../store/useStore'
import { generateSynthetic, listVectors } from '../services/api'

const methods = [
  { value: 'smote', label: 'SMOTE', description: 'Synthetic Minority Oversampling' },
  { value: 'noise', label: 'Noise', description: 'Gaussian noise injection' },
  { value: 'jitter', label: 'Jitter', description: 'Uniform random jitter' },
  { value: 'interpolate', label: 'Interpolate', description: 'Multi-point interpolation' },
  { value: 'adasyn', label: 'ADASYN', description: 'Adaptive synthetic sampling' },
]

function SyntheticPage() {
  const { vectors } = useStore()
  const [generating, setGenerating] = useState(false)
  const [syntheticVectors, setSyntheticVectors] = useState([])
  const [method, setMethod] = useState('smote')
  const [count, setCount] = useState(10)
  const [error, setError] = useState(null)
  const [selectedReal, setSelectedReal] = useState(null)
  const [selectedSynthetic, setSelectedSynthetic] = useState(null)

  const handleGenerate = async () => {
    setGenerating(true)
    setError(null)

    try {
      const storedResult = await listVectors()
      const sourceVectors = storedResult.vectors?.map((v) => v.vector) || []

      if (sourceVectors.length === 0) {
        setError('No source vectors available. Please upload and extract features first.')
        setGenerating(false)
        return
      }

      const result = await generateSynthetic(sourceVectors, count, method, true)

      if (result.success) {
        setSyntheticVectors(
          result.synthetic_vectors.map((vec, idx) => ({
            id: `synthetic_${idx}`,
            vector: vec,
            method: result.method,
          }))
        )
      } else {
        setError(result.error || 'Generation failed')
      }
    } catch (err) {
      setError(err.message || 'Generation failed')
    } finally {
      setGenerating(false)
    }
  }

  const computeStats = (vector) => {
    if (!vector || vector.length === 0) return { mean: 0, std: 0, min: 0, max: 0 }
    const mean = vector.reduce((a, b) => a + b, 0) / vector.length
    const variance = vector.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / vector.length
    return {
      mean: mean,
      std: Math.sqrt(variance),
      min: Math.min(...vector),
      max: Math.max(...vector),
    }
  }

  const computeSimilarity = (vec1, vec2) => {
    if (!vec1 || !vec2 || vec1.length !== vec2.length) return 0
    let dotProduct = 0, norm1 = 0, norm2 = 0
    for (let i = 0; i < vec1.length; i++) {
      dotProduct += vec1[i] * vec2[i]
      norm1 += vec1[i] * vec1[i]
      norm2 += vec2[i] * vec2[i]
    }
    const magnitude = Math.sqrt(norm1) * Math.sqrt(norm2)
    return magnitude === 0 ? 0 : dotProduct / magnitude
  }

  const comparisonPlot = React.useMemo(() => {
    if (!selectedReal || !selectedSynthetic) return null

    const realStats = computeStats(selectedReal.vector)
    const synthStats = computeStats(selectedSynthetic.vector)

    return {
      data: [
        {
          type: 'bar',
          name: 'Real',
          x: ['Mean', 'Std Dev', 'Min', 'Max'],
          y: [realStats.mean, realStats.std, realStats.min, realStats.max],
          marker: { color: '#4CAF50' },
        },
        {
          type: 'bar',
          name: 'Synthetic',
          x: ['Mean', 'Std Dev', 'Min', 'Max'],
          y: [synthStats.mean, synthStats.std, synthStats.min, synthStats.max],
          marker: { color: '#2196F3' },
        },
      ],
      layout: {
        barmode: 'group',
        margin: { t: 30, b: 40, l: 50, r: 20 },
        height: 250,
        legend: { orientation: 'h', y: 1.1 },
      },
    }
  }, [selectedReal, selectedSynthetic])

  const distributionPlot = React.useMemo(() => {
    if (syntheticVectors.length === 0) return null

    const allMeans = syntheticVectors.map((v) => computeStats(v.vector).mean)

    return {
      data: [
        {
          type: 'histogram',
          x: allMeans,
          nbinsx: 20,
          marker: { color: '#2196F3' },
          name: 'Synthetic Means',
        },
      ],
      layout: {
        margin: { t: 30, b: 40, l: 50, r: 20 },
        height: 200,
        xaxis: { title: 'Mean Value' },
        yaxis: { title: 'Count' },
      },
    }
  }, [syntheticVectors])

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Synthetic Data Generator</h2>
        <p className="text-gray-600 mb-6">Generate synthetic behavior vectors for data augmentation</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Generation Method
            </label>
            <div className="space-y-2">
              {methods.map((m) => (
                <label
                  key={m.value}
                  className={`flex items-start p-3 border rounded-lg cursor-pointer transition-colors ${
                    method === m.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="method"
                    value={m.value}
                    checked={method === m.value}
                    onChange={(e) => setMethod(e.target.value)}
                    className="mt-1 mr-3"
                  />
                  <div>
                    <div className="font-medium">{m.label}</div>
                    <div className="text-xs text-gray-500">{m.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Vectors
            </label>
            <input
              type="range"
              min={1}
              max={50}
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="text-center text-2xl font-bold text-primary-600 mt-2">{count}</div>
          </div>

          <div className="flex flex-col justify-end">
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="btn-primary flex items-center justify-center"
            >
              {generating ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  Generate Vectors
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
      </div>

      {syntheticVectors.length > 0 && (
        <>
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Generated Vectors ({syntheticVectors.length})
              </h3>
              <span className="text-sm text-gray-500">Method: {method.toUpperCase()}</span>
            </div>

            {distributionPlot && (
              <Plot
                data={distributionPlot.data}
                layout={distributionPlot.layout}
                config={{ responsive: true, displayModeBar: false }}
                className="w-full"
              />
            )}

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mt-4">
              {syntheticVectors.slice(0, 12).map((vec) => {
                const stats = computeStats(vec.vector)
                const isSelected = selectedSynthetic?.id === vec.id

                return (
                  <button
                    key={vec.id}
                    onClick={() => setSelectedSynthetic(isSelected ? null : vec)}
                    className={`p-3 rounded-lg border text-left transition-colors ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-xs font-medium text-gray-600">{vec.id}</div>
                    <div className="text-sm font-semibold mt-1">μ: {stats.mean.toFixed(3)}</div>
                    <div className="text-xs text-gray-500">σ: {stats.std.toFixed(3)}</div>
                  </button>
                )
              })}
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Compare Real vs Synthetic</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Select Real Vector</h4>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {vectors.map((vec) => {
                    const stats = computeStats(vec.vector)
                    const isSelected = selectedReal?.id === vec.id

                    return (
                      <button
                        key={vec.id}
                        onClick={() => setSelectedReal(isSelected ? null : vec)}
                        className={`w-full p-3 rounded-lg border text-left transition-colors ${
                          isSelected
                            ? 'border-green-500 bg-green-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex justify-between">
                          <span className="text-sm font-medium">{vec.id}</span>
                          <span className="text-xs text-green-600">Real</span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          μ: {stats.mean.toFixed(3)} | σ: {stats.std.toFixed(3)}
                        </div>
                      </button>
                    )
                  })}
                  {vectors.length === 0 && (
                    <p className="text-gray-500 text-sm">No real vectors available</p>
                  )}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Select Synthetic Vector</h4>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {syntheticVectors.map((vec) => {
                    const stats = computeStats(vec.vector)
                    const isSelected = selectedSynthetic?.id === vec.id

                    return (
                      <button
                        key={vec.id}
                        onClick={() => setSelectedSynthetic(isSelected ? null : vec)}
                        className={`w-full p-3 rounded-lg border text-left transition-colors ${
                          isSelected
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex justify-between">
                          <span className="text-sm font-medium">{vec.id}</span>
                          <span className="text-xs text-blue-600">Synthetic</span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          μ: {stats.mean.toFixed(3)} | σ: {stats.std.toFixed(3)}
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>

            {selectedReal && selectedSynthetic && (
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <div className="text-center mb-4">
                  <span className="text-sm text-gray-500">Cosine Similarity</span>
                  <div className="text-3xl font-bold text-primary-600">
                    {computeSimilarity(selectedReal.vector, selectedSynthetic.vector).toFixed(4)}
                  </div>
                </div>

                {comparisonPlot && (
                  <Plot
                    data={comparisonPlot.data}
                    layout={comparisonPlot.layout}
                    config={{ responsive: true, displayModeBar: false }}
                    className="w-full"
                  />
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default SyntheticPage
