import React, { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import Plot from 'react-plotly.js'
import { BarChart3, ChevronDown, ChevronRight } from 'lucide-react'
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
}

function AnalysisPage() {
  const navigate = useNavigate()
  const { currentVector, featureLabels, categories } = useStore()
  const [expandedCategories, setExpandedCategories] = React.useState({})

  const toggleCategory = (cat) => {
    setExpandedCategories((prev) => ({ ...prev, [cat]: !prev[cat] }))
  }

  const radarData = useMemo(() => {
    if (!categories) return null

    const categoryMeans = Object.entries(categories).map(([cat, features]) => {
      const values = Object.values(features).filter((v) => typeof v === 'number')
      return {
        category: cat,
        mean: values.reduce((a, b) => a + b, 0) / values.length,
      }
    })

    return {
      data: [
        {
          type: 'scatterpolar',
          r: categoryMeans.map((c) => c.mean),
          theta: categoryMeans.map((c) => c.category),
          fill: 'toself',
          fillcolor: 'rgba(14, 165, 233, 0.2)',
          line: { color: '#0ea5e9' },
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
  }, [categories])

  const barData = useMemo(() => {
    if (!categories) return null

    const allFeatures = []
    Object.entries(categories).forEach(([cat, features]) => {
      Object.entries(features).forEach(([name, value]) => {
        allFeatures.push({ name, value, category: cat })
      })
    })

    const topFeatures = allFeatures
      .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
      .slice(0, 20)

    return {
      data: [
        {
          type: 'bar',
          x: topFeatures.map((f) => f.value),
          y: topFeatures.map((f) => f.name.replace(/_/g, ' ')),
          orientation: 'h',
          marker: {
            color: topFeatures.map((f) => categoryColors[f.category] || '#999'),
          },
        },
      ],
      layout: {
        margin: { t: 20, b: 40, l: 150, r: 20 },
        height: 500,
        xaxis: { title: 'Value' },
        yaxis: { automargin: true },
      },
    }
  }, [categories])

  if (!currentVector || !featureLabels) {
    return (
      <div className="text-center py-20">
        <BarChart3 className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h2 className="text-xl font-semibold text-gray-600 mb-2">No Analysis Data</h2>
        <p className="text-gray-500 mb-6">Upload a chat log to see analysis results</p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Upload Chat Log
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Behavior Vector Analysis</h2>
        <p className="text-gray-600">{currentVector.length} features extracted</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Radar</h3>
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
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Features</h3>
          {barData && (
            <Plot
              data={barData.data}
              layout={barData.layout}
              config={{ responsive: true, displayModeBar: false }}
              className="w-full"
            />
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Features by Category</h3>
        <div className="space-y-2">
          {categories &&
            Object.entries(categories).map(([cat, features]) => {
              const isExpanded = expandedCategories[cat]
              const featureCount = Object.keys(features).length
              const avgValue =
                Object.values(features).reduce((a, b) => a + (typeof b === 'number' ? b : 0), 0) /
                featureCount

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
    </div>
  )
}

export default AnalysisPage
