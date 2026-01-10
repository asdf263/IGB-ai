import React, { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import CytoscapeComponent from 'react-cytoscapejs'
import { Network, Loader2, RefreshCw, ZoomIn, ZoomOut } from 'lucide-react'
import useStore from '../store/useStore'
import { getVisualizationGraph, clusterVectors } from '../services/api'

const clusterColors = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
  '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
]

function ClusterPage() {
  const navigate = useNavigate()
  const { clusterData, setClusterData } = useStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [clusterMethod, setClusterMethod] = useState('kmeans')
  const [reduceMethod, setReduceMethod] = useState('pca')
  const [nClusters, setNClusters] = useState(5)
  const cyRef = useRef(null)

  const loadGraph = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await getVisualizationGraph()
      if (result.success) {
        setClusterData(result)
      } else {
        setError(result.error || 'Failed to load graph')
      }
    } catch (err) {
      setError(err.message || 'Failed to load graph')
    } finally {
      setLoading(false)
    }
  }

  const runClustering = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await clusterVectors({
        clusterMethod,
        reduceMethod,
        nClusters,
      })
      if (result.success) {
        await loadGraph()
      } else {
        setError(result.error || 'Clustering failed')
      }
    } catch (err) {
      setError(err.message || 'Clustering failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadGraph()
  }, [])

  const cytoscapeElements = React.useMemo(() => {
    if (!clusterData || !clusterData.nodes) return []

    const elements = []

    clusterData.nodes.forEach((node) => {
      elements.push({
        data: {
          id: node.id,
          label: node.id.replace('node_', ''),
          cluster: node.cluster,
          ...node.vector_summary,
        },
        position: { x: node.x * 5, y: node.y * 5 },
      })
    })

    if (clusterData.edges) {
      clusterData.edges.forEach((edge) => {
        elements.push({
          data: {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            weight: edge.weight,
          },
        })
      })
    }

    return elements
  }, [clusterData])

  const cytoscapeStylesheet = [
    {
      selector: 'node',
      style: {
        'background-color': (ele) => clusterColors[ele.data('cluster') % clusterColors.length],
        label: 'data(label)',
        'text-valign': 'bottom',
        'text-halign': 'center',
        'font-size': '10px',
        width: 30,
        height: 30,
      },
    },
    {
      selector: 'node:selected',
      style: {
        'border-width': 3,
        'border-color': '#000',
      },
    },
    {
      selector: 'edge',
      style: {
        width: (ele) => Math.max(1, ele.data('weight') * 3),
        'line-color': '#ccc',
        'curve-style': 'bezier',
        opacity: 0.5,
      },
    },
  ]

  const handleNodeClick = (event) => {
    const node = event.target
    setSelectedNode({
      id: node.id(),
      cluster: node.data('cluster'),
      mean: node.data('mean'),
      std: node.data('std'),
      max: node.data('max'),
      min: node.data('min'),
    })
  }

  const handleZoomIn = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 1.2)
    }
  }

  const handleZoomOut = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() / 1.2)
    }
  }

  const handleFit = () => {
    if (cyRef.current) {
      cyRef.current.fit()
    }
  }

  if (loading && !clusterData) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        <span className="ml-3 text-gray-600">Loading cluster graph...</span>
      </div>
    )
  }

  if (error && !clusterData) {
    return (
      <div className="text-center py-20">
        <Network className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h2 className="text-xl font-semibold text-gray-600 mb-2">Error Loading Graph</h2>
        <p className="text-red-500 mb-6">{error}</p>
        <div className="space-x-4">
          <button onClick={loadGraph} className="btn-primary">
            Retry
          </button>
          <button onClick={() => navigate('/')} className="btn-secondary">
            Upload Data
          </button>
        </div>
      </div>
    )
  }

  if (!clusterData || clusterData.nodes?.length === 0) {
    return (
      <div className="text-center py-20">
        <Network className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h2 className="text-xl font-semibold text-gray-600 mb-2">No Vectors to Visualize</h2>
        <p className="text-gray-500 mb-6">Upload and extract features first</p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Upload Chat Log
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Cluster Visualization</h2>
            <p className="text-gray-600">
              {clusterData.nodes?.length || 0} vectors • {clusterData.clusters?.length || 0} clusters
            </p>
          </div>
          <button
            onClick={loadGraph}
            disabled={loading}
            className="btn-secondary flex items-center"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cluster Method
            </label>
            <select
              value={clusterMethod}
              onChange={(e) => setClusterMethod(e.target.value)}
              className="input"
            >
              <option value="kmeans">K-Means</option>
              <option value="hdbscan">HDBSCAN</option>
              <option value="agglomerative">Agglomerative</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reduction Method
            </label>
            <select
              value={reduceMethod}
              onChange={(e) => setReduceMethod(e.target.value)}
              className="input"
            >
              <option value="pca">PCA</option>
              <option value="umap">UMAP</option>
              <option value="tsne">t-SNE</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Clusters
            </label>
            <input
              type="number"
              value={nClusters}
              onChange={(e) => setNClusters(parseInt(e.target.value) || 5)}
              min={2}
              max={20}
              className="input"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={runClustering}
              disabled={loading}
              className="btn-primary w-full"
            >
              {loading ? 'Running...' : 'Run Clustering'}
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 card p-0 overflow-hidden">
          <div className="flex items-center justify-end p-2 border-b border-gray-200 bg-gray-50">
            <button onClick={handleZoomIn} className="p-2 hover:bg-gray-200 rounded">
              <ZoomIn className="w-5 h-5" />
            </button>
            <button onClick={handleZoomOut} className="p-2 hover:bg-gray-200 rounded">
              <ZoomOut className="w-5 h-5" />
            </button>
            <button onClick={handleFit} className="p-2 hover:bg-gray-200 rounded text-sm">
              Fit
            </button>
          </div>
          <div className="h-[500px]">
            <CytoscapeComponent
              elements={cytoscapeElements}
              stylesheet={cytoscapeStylesheet}
              style={{ width: '100%', height: '100%' }}
              cy={(cy) => {
                cyRef.current = cy
                cy.on('tap', 'node', handleNodeClick)
              }}
              layout={{ name: 'preset' }}
            />
          </div>
        </div>

        <div className="space-y-4">
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-3">Clusters</h3>
            <div className="space-y-2">
              {clusterData.clusters?.map((cluster) => (
                <div key={cluster.id} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div
                      className="w-3 h-3 rounded-full mr-2"
                      style={{ backgroundColor: cluster.color }}
                    />
                    <span className="text-sm">Cluster {cluster.id}</span>
                  </div>
                  <span className="text-sm text-gray-500">{cluster.count} vectors</span>
                </div>
              ))}
            </div>
          </div>

          {selectedNode && (
            <div className="card">
              <h3 className="font-semibold text-gray-900 mb-3">Selected Node</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">ID</span>
                  <span>{selectedNode.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Cluster</span>
                  <span>{selectedNode.cluster}</span>
                </div>
                {selectedNode.mean !== undefined && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Mean</span>
                      <span>{selectedNode.mean?.toFixed(4)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Std</span>
                      <span>{selectedNode.std?.toFixed(4)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Range</span>
                      <span>
                        [{selectedNode.min?.toFixed(2)}, {selectedNode.max?.toFixed(2)}]
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ClusterPage
