import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { MessageCircle, Send, Loader2, User, Bot, AlertCircle, Users } from 'lucide-react'
import { listEcosystemPersonas, chatWithPersona } from '../services/api'

function ChatPage() {
  const navigate = useNavigate()
  const [personas, setPersonas] = useState([])
  const [selectedPersona, setSelectedPersona] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingPersonas, setLoadingPersonas] = useState(true)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    loadPersonas()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadPersonas = async () => {
    setLoadingPersonas(true)
    try {
      const result = await listEcosystemPersonas()
      if (result.success) {
        setPersonas(result.personas)
      }
    } catch (err) {
      setError('Failed to load personas')
    } finally {
      setLoadingPersonas(false)
    }
  }

  const handleSelectPersona = (persona) => {
    setSelectedPersona(persona)
    setMessages([
      {
        role: 'system',
        content: `You are now chatting with ${persona.user_name}'s AI persona. This AI has been trained on their conversation patterns and personality traits. Feel free to explore how they communicate!`,
      },
    ])
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedPersona || loading) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setError(null)

    // Add user message
    const newMessages = [...messages, { role: 'user', content: userMessage }]
    setMessages(newMessages)

    setLoading(true)
    try {
      // Build conversation history for context
      const history = newMessages
        .filter((m) => m.role !== 'system')
        .map((m) => ({ role: m.role, content: m.content }))

      const result = await chatWithPersona(selectedPersona.persona_id, userMessage, history)

      if (result.success) {
        setMessages([...newMessages, { role: 'assistant', content: result.response }])
      } else {
        setError('Failed to get response')
      }
    } catch (err) {
      setError(err.message || 'Failed to send message')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  if (loadingPersonas) {
    return (
      <div className="text-center py-20">
        <Loader2 className="w-12 h-12 mx-auto text-sky-500 animate-spin mb-4" />
        <p className="text-gray-600">Loading personas...</p>
      </div>
    )
  }

  if (personas.length === 0) {
    return (
      <div className="text-center py-20">
        <MessageCircle className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h2 className="text-xl font-semibold text-gray-600 mb-2">No Personas Available</h2>
        <p className="text-gray-500 mb-6">
          Add personas to the ecosystem first to start chatting
        </p>
        <button onClick={() => navigate('/ecosystem')} className="btn-primary">
          Go to Ecosystem
        </button>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-12rem)] flex gap-6">
      {/* Persona Selection Sidebar */}
      <div className="w-64 flex-shrink-0">
        <div className="card h-full overflow-hidden flex flex-col">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
            <Users className="w-5 h-5 mr-2 text-sky-500" />
            AI Personas
          </h3>
          <div className="flex-1 overflow-y-auto space-y-2">
            {personas.map((persona) => (
              <button
                key={persona.persona_id}
                onClick={() => handleSelectPersona(persona)}
                className={`w-full p-3 rounded-lg text-left transition-colors ${
                  selectedPersona?.persona_id === persona.persona_id
                    ? 'bg-sky-100 border-2 border-sky-300'
                    : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                }`}
              >
                <div className="font-medium text-gray-900">{persona.user_name}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {persona.interaction_count || 0} chats
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedPersona ? (
          <>
            {/* Chat Header */}
            <div className="card mb-4">
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-sky-400 to-purple-500 flex items-center justify-center text-white font-bold">
                  {selectedPersona.user_name.charAt(0).toUpperCase()}
                </div>
                <div className="ml-3">
                  <h2 className="font-semibold text-gray-900">
                    {selectedPersona.user_name}'s AI Persona
                  </h2>
                  <p className="text-sm text-gray-500">
                    Preview interpersonal dynamics before meeting in person
                  </p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 card overflow-hidden flex flex-col">
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.role === 'system' ? (
                      <div className="bg-gray-100 text-gray-600 text-sm p-3 rounded-lg max-w-lg text-center mx-auto">
                        {message.content}
                      </div>
                    ) : (
                      <div
                        className={`flex items-start max-w-[70%] ${
                          message.role === 'user' ? 'flex-row-reverse' : ''
                        }`}
                      >
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                            message.role === 'user'
                              ? 'bg-sky-500 ml-2'
                              : 'bg-purple-500 mr-2'
                          }`}
                        >
                          {message.role === 'user' ? (
                            <User className="w-4 h-4 text-white" />
                          ) : (
                            <Bot className="w-4 h-4 text-white" />
                          )}
                        </div>
                        <div
                          className={`p-3 rounded-lg ${
                            message.role === 'user'
                              ? 'bg-sky-500 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          {message.content}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="flex items-center bg-gray-100 p-3 rounded-lg">
                      <Loader2 className="w-4 h-4 animate-spin text-gray-500 mr-2" />
                      <span className="text-gray-500">Thinking...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Error */}
              {error && (
                <div className="px-4 py-2 bg-red-50 border-t border-red-200 flex items-center text-red-700 text-sm">
                  <AlertCircle className="w-4 h-4 mr-2" />
                  {error}
                </div>
              )}

              {/* Input */}
              <div className="p-4 border-t border-gray-200">
                <div className="flex gap-2">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={`Message ${selectedPersona.user_name}...`}
                    className="input flex-1 resize-none"
                    rows={1}
                    disabled={loading}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={loading || !inputMessage.trim()}
                    className="btn-primary px-4 disabled:opacity-50"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 card flex items-center justify-center">
            <div className="text-center">
              <MessageCircle className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-semibold text-gray-600 mb-2">
                Select a Persona to Chat
              </h3>
              <p className="text-gray-500">
                Choose an AI persona from the sidebar to start a conversation
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatPage
