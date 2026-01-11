import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, FileJson, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import useStore from '../store/useStore'
import { extractFeatures, extractUserFeatures, saveAnalysis } from '../services/api'

function UploadPage() {
  const navigate = useNavigate()
  const { setCurrentVector, setFeatureLabels, setCategories, addVector, setUserFeatures, setCurrentMessages } = useStore()
  const [jsonText, setJsonText] = useState('')
  const [inputMode, setInputMode] = useState('file')
  const [validationStatus, setValidationStatus] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)

  const validateJson = (text) => {
    try {
      const parsed = JSON.parse(text)
      if (!parsed.messages || !Array.isArray(parsed.messages)) {
        setValidationStatus('invalid')
        return null
      }
      setValidationStatus('valid')
      return parsed
    } catch {
      setValidationStatus('invalid')
      return null
    }
  }

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const text = e.target.result
        setJsonText(text)
        validateJson(text)
      }
      reader.readAsText(file)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/json': ['.json'] },
    multiple: false,
  })

  const handleJsonChange = (e) => {
    const text = e.target.value
    setJsonText(text)
    if (text.trim()) {
      validateJson(text)
    } else {
      setValidationStatus(null)
    }
  }

  const handleExtract = async () => {
    setUploading(true)
    setError(null)

    try {
      const parsed = validateJson(jsonText)
      if (!parsed) {
        setError('Invalid JSON format')
        setUploading(false)
        return
      }

      // Extract standard features
      const result = await extractFeatures(parsed.messages, true)

      // Also extract user-based features
      const userResult = await extractUserFeatures(parsed.messages)

      if (result.success) {
        setCurrentVector(result.vector)
        setFeatureLabels(result.feature_labels)
        setCategories(result.categories)
        addVector({
          id: result.vector_id,
          vector: result.vector,
          labels: result.feature_labels,
          categories: result.categories,
          timestamp: new Date().toISOString(),
        })

        // Store user features and messages for user profile and compatibility pages
        if (userResult.success) {
          setUserFeatures(userResult)
          setCurrentMessages(parsed.messages)
          
          // Save analysis to local storage (creates new file each time)
          try {
            const saveResult = await saveAnalysis(
              parsed.messages,
              userResult.users,
              null,
              {
                vector: result.vector,
                labels: result.feature_labels,
                categories: result.categories,
              }
            )
            console.log('Analysis saved:', saveResult.analysis_id)
          } catch (saveErr) {
            console.warn('Failed to save analysis:', saveErr)
          }
        }

        navigate('/analysis')
      } else {
        setError(result.error || 'Extraction failed')
      }
    } catch (err) {
      setError(err.message || 'Failed to extract features')
    } finally {
      setUploading(false)
    }
  }

  const sampleJson = `{
  "messages": [
    {"sender": "user", "text": "Hello!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Hi there!", "timestamp": 1715234012}
  ]
}`

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Chat Log</h2>
        <p className="text-gray-600 mb-6">Get started on your optimized matchmaking!</p>

        <div className="flex space-x-2 mb-6">
          <button
            onClick={() => setInputMode('file')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              inputMode === 'file'
                ? 'bg-rose-100 text-rose-700'
                : 'bg-rose-50 text-rose-600 hover:bg-rose-100'
            }`}
          >
            File Upload
          </button>
          <button
            onClick={() => setInputMode('text')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              inputMode === 'text'
                ? 'bg-rose-100 text-rose-700'
                : 'bg-rose-50 text-rose-600 hover:bg-rose-100'
            }`}
          >
            Paste JSON
          </button>
        </div>

        {inputMode === 'file' ? (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-rose-500 bg-rose-50'
                : 'border-rose-300 hover:border-rose-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 mx-auto text-rose-300 mb-4" />
            {isDragActive ? (
              <p className="text-rose-600 font-medium">Drop the file here...</p>
            ) : (
              <>
                <p className="text-gray-700 font-medium">
                  Drag & drop a JSON file here, or click to select
                </p>
                <p className="text-rose-400 text-sm mt-2">Only .json files are accepted</p>
              </>
            )}
          </div>
        ) : (
          <div>
            <textarea
              value={jsonText}
              onChange={handleJsonChange}
              placeholder={sampleJson}
              className="input font-mono text-sm h-64 resize-none"
            />
          </div>
        )}

        {jsonText && (
          <div className="mt-4 flex items-center">
            {validationStatus === 'valid' ? (
              <div className="flex items-center text-green-600">
                <CheckCircle className="w-5 h-5 mr-2" />
                <span>Valid JSON format</span>
              </div>
            ) : validationStatus === 'invalid' ? (
              <div className="flex items-center text-red-600">
                <AlertCircle className="w-5 h-5 mr-2" />
                <span>Invalid JSON - must contain messages array</span>
              </div>
            ) : null}
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        <button
          onClick={handleExtract}
          disabled={uploading || validationStatus !== 'valid'}
          className="btn-primary w-full mt-6 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Extracting Features...
            </>
          ) : (
            <>
              <FileJson className="w-5 h-5 mr-2" />
              Extract Features
            </>
          )}
        </button>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Expected Format</h3>
        <pre className="bg-rose-50 p-4 rounded-lg text-sm font-mono overflow-x-auto border border-rose-100">
          {sampleJson}
        </pre>
      </div>
    </div>
  )
}

export default UploadPage
