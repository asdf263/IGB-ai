import React, { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import Plot from 'react-plotly.js'
import { 
  BarChart3, 
  ChevronDown, 
  ChevronRight, 
  Type, 
  MessageSquare, 
  BookOpen, 
  Calendar, 
  Shuffle, 
  Clock,
  Info
} from 'lucide-react'
import useStore from '../store/useStore'

const categoryColors = {
  temporal: '#E8B4B4',        // Soft rose
  text: '#F4A5B8',            // Soft pink
  linguistic: '#D4A5C4',      // Soft lavender
  semantic: '#E8B4D4',        // Soft mauve
  sentiment: '#F4C5D4',       // Soft blush
  behavioral: '#D49AC4',      // Soft magenta
  graph: '#E8C4D4',           // Soft rose-pink
  composite: '#F4D4C5',       // Soft peach
}

const categoryDescriptions = {
  temporal: 'Time-based patterns: response times, message frequency, session duration, and timing patterns',
  text: 'Text structure metrics: message length, word counts, punctuation, and formatting features',
  linguistic: 'Language style: sentence complexity, readability, grammar patterns, and vocabulary diversity',
  semantic: 'Meaning and content: topic modeling, keyword frequency, content diversity, and topic coherence',
  sentiment: 'Emotional content: sentiment scores, emotion categories, and emotional dynamics',
  behavioral: 'Social behavior: response rates, politeness, engagement levels, and interaction patterns',
  graph: 'Conversation structure: relationship patterns, message connections, and network metrics',
  composite: 'Derived scores: overall behavior indicators combining multiple feature categories',
}

function AnalysisPage() {
  const navigate = useNavigate()
  const { currentVector, featureLabels, categories } = useStore()
  const [expandedCategories, setExpandedCategories] = React.useState({})

  const toggleCategory = (cat) => {
    setExpandedCategories((prev) => ({ ...prev, [cat]: !prev[cat] }))
  }

  const barChartData = useMemo(() => {
    if (!categories) return null

    const categoryMeans = Object.entries(categories).map(([cat, features]) => {
      const values = Object.values(features).filter((v) => typeof v === 'number')
      return {
        category: cat,
        mean: values.reduce((a, b) => a + b, 0) / values.length,
      }
    })

    // Sort by category name for consistent display
    categoryMeans.sort((a, b) => a.category.localeCompare(b.category))

    // Calculate overall average
    const overallAverage = categoryMeans.reduce((sum, c) => sum + c.mean, 0) / categoryMeans.length

    return {
      data: [
        {
          type: 'bar',
          x: categoryMeans.map((c) => c.category.charAt(0).toUpperCase() + c.category.slice(1)),
          y: categoryMeans.map((c) => c.mean),
          marker: {
            color: categoryMeans.map((c) => categoryColors[c.category] || '#CCCCCC'),
          },
          text: categoryMeans.map((c) => c.mean.toFixed(3)),
          textposition: 'outside',
          name: 'Category Scores',
        },
        {
          type: 'scatter',
          x: categoryMeans.map((c) => c.category.charAt(0).toUpperCase() + c.category.slice(1)),
          y: new Array(categoryMeans.length).fill(overallAverage),
          mode: 'lines',
          line: {
            color: '#666666',
            width: 2,
            dash: 'solid',
          },
          showlegend: false,
          hoverinfo: 'skip',
        },
      ],
      layout: {
        margin: { t: 20, b: 80, l: 60, r: 20 },
        height: 350,
        xaxis: { 
          title: {
            text: 'Category',
            standoff: 20,
          },
          tickangle: -45,
        },
        yaxis: { 
          title: 'Average Score',
          range: [0, 1],
        },
        showlegend: false,
        annotations: [
          {
            x: categoryMeans.length - 0.5,
            y: overallAverage,
            xref: 'x',
            yref: 'y',
            text: `Avg: ${overallAverage.toFixed(3)}`,
            showarrow: false,
            xanchor: 'right',
            yanchor: 'bottom',
            bgcolor: 'rgba(255, 255, 255, 0.8)',
            bordercolor: '#666666',
            borderwidth: 1,
            borderpad: 4,
            font: {
              size: 10,
              color: '#666666',
            },
          },
        ],
      },
    }
  }, [categories])

  const topFeatures = useMemo(() => {
    if (!categories) return []

    const featureMap = {
      'avg_sentence_length': {
        key: 'avg_sentence_length',
        category: 'linguistic',
        label: 'Avg Sentence Length',
        unit: 'words',
        description: 'Average number of words per sentence, indicating communication style complexity',
        icon: Type,
        color: categoryColors.linguistic,
      },
      'msg_length_mean': {
        key: 'msg_length_mean',
        category: 'text',
        label: 'Msg Length Mean',
        unit: 'chars',
        description: 'Average message length in characters, showing typical message size',
        icon: MessageSquare,
        color: categoryColors.text,
      },
      'readability_score': {
        key: 'readability_score',
        category: 'linguistic',
        label: 'Readability Score',
        unit: '/100',
        description: 'Flesch-Kincaid readability score (0-100). Higher scores indicate easier-to-read text',
        icon: BookOpen,
        color: categoryColors.linguistic,
      },
      'avg_messages_per_day': {
        key: 'avg_messages_per_day',
        category: 'temporal',
        label: 'Average Messages Per Day',
        unit: 'msgs/day',
        description: 'Average number of messages sent per day, indicating communication frequency',
        icon: Calendar,
        color: categoryColors.temporal,
      },
      'topic_switch_count': {
        key: 'topic_switch_count',
        category: 'semantic',
        label: 'Topic Switch Count',
        unit: '',
        description: 'Number of times conversation topics changed, showing discussion diversity',
        icon: Shuffle,
        color: categoryColors.semantic,
      },
      'avg_session_length': {
        key: 'avg_session_length',
        category: 'temporal',
        label: 'Average Session Length',
        unit: 'msgs',
        description: 'Average number of messages per conversation session',
        icon: Clock,
        color: categoryColors.temporal,
      },
    }

    const features = []
    Object.entries(featureMap).forEach(([_, config]) => {
      const categoryData = categories[config.category]
      if (categoryData && categoryData[config.key] !== undefined) {
        features.push({
          ...config,
          value: categoryData[config.key],
          Icon: config.icon,
        })
      }
    })

    return features
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
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Stand Out Data</h3>
          {topFeatures.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {topFeatures.map((feature) => {
                const Icon = feature.Icon
                return (
                  <div
                    key={feature.key}
                    className="bg-white border-2 rounded-lg p-4 hover:shadow-md transition-shadow group relative"
                    style={{ borderColor: feature.color }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <Icon className="w-6 h-6" style={{ color: feature.color }} />
                    </div>
                    <div className="text-xs text-gray-500 mb-1">{feature.label}</div>
                    <div className="text-xl font-bold text-gray-900 mb-1">
                      {typeof feature.value === 'number' 
                        ? feature.value.toFixed(2) 
                        : feature.value}
                      <span className="text-sm font-normal text-gray-500 ml-1">{feature.unit}</span>
                    </div>
                    <div className="text-xs text-gray-400 mt-2 leading-relaxed">
                      {feature.description}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Scores</h3>
          {barChartData && (
            <>
              <Plot
                data={barChartData.data}
                layout={barChartData.layout}
                config={{ responsive: true, displayModeBar: false }}
                className="w-full"
              />
              <div className="mt-6 pt-4 border-t border-rose-200">
                <h4 className="text-sm font-semibold text-rose-700 mb-3">Category Key</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {categories && Object.keys(categories).sort().map((cat) => (
                    <div key={cat} className="flex items-start gap-2">
                      <div
                        className="w-3 h-3 rounded-full mt-1 flex-shrink-0"
                        style={{ backgroundColor: categoryColors[cat] || '#999' }}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900 capitalize mb-0.5">
                          {cat}
                        </div>
                        <div className="text-xs text-rose-600 leading-relaxed">
                          {categoryDescriptions[cat] || 'Category description'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
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
                <div key={cat} className="border border-rose-200 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleCategory(cat)}
                    className="w-full flex items-center justify-between p-4 hover:bg-rose-50 transition-colors"
                  >
                    <div className="flex items-center">
                      <div
                        className="w-3 h-3 rounded-full mr-3"
                        style={{ backgroundColor: categoryColors[cat] || '#999' }}
                      />
                      <span className="font-medium capitalize text-gray-900">{cat}</span>
                      <span className="ml-2 text-sm text-rose-600">
                        {featureCount} features • avg: {avgValue.toFixed(3)}
                      </span>
                    </div>
                    {isExpanded ? (
                      <ChevronDown className="w-5 h-5 text-rose-400" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-rose-400" />
                    )}
                  </button>

                  {isExpanded && (
                    <div className="border-t border-rose-200 bg-rose-50 p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {Object.entries(features).map(([name, value]) => (
                          <div key={name} className="bg-white p-3 rounded border border-rose-200">
                            <div className="text-xs text-rose-600 capitalize">
                              {name.replace(/_/g, ' ')}
                            </div>
                            <div className="text-lg font-semibold text-gray-900">
                              {typeof value === 'number' ? value.toFixed(4) : value}
                            </div>
                            <div className="mt-1 h-1 bg-rose-100 rounded overflow-hidden">
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
