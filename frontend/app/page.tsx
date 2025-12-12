'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Paperclip, Sidebar, MessageSquare, Plus, Trash2, Copy, CheckCircle, FileText } from 'lucide-react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

const API_URL = 'http://127.0.0.1:8000'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: any[]
  activeDocuments?: string[]  // Documents available when this message was sent
}

interface ChatSession {
  id: string
  title: string
  messages: Message[]
  documents: string[]  // Document filenames for this chat
  createdAt: string
  lastMessageAt: string
}

export default function ChatPage() {
  const [chats, setChats] = useState<ChatSession[]>([])
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const [uploadingFiles, setUploadingFiles] = useState<string[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Get current chat
  const currentChat = chats.find(c => c.id === currentChatId)
  const messages = currentChat?.messages || []
  const documents = currentChat?.documents || []

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Create new chat
  const createNewChat = () => {
    const newChat: ChatSession = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
      documents: [],
      createdAt: new Date().toISOString(),
      lastMessageAt: new Date().toISOString()
    }
    setChats([newChat, ...chats])
    setCurrentChatId(newChat.id)
  }

  // Generate chat title from first message
  const generateChatTitle = (firstMessage: string) => {
    return firstMessage.length > 40 ? firstMessage.substring(0, 40) + '...' : firstMessage
  }

  // Handle file upload - scoped to current chat
  const handleFileUpload = async (files: FileList) => {
    if (!currentChatId) {
      alert('Please start a chat first')
      return
    }

    const fileNames = Array.from(files).map(f => f.name)
    setUploadingFiles(fileNames)

    const formData = new FormData()
    Array.from(files).forEach(file => {
      formData.append('files', file)
    })

    try {
      const response = await axios.post(`${API_URL}/documents/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      // Add documents to current chat only
      setChats(chats.map(chat => 
        chat.id === currentChatId 
          ? { ...chat, documents: [...chat.documents, ...fileNames] }
          : chat
      ))

      console.log('✅ Documents uploaded successfully:', response.data)
    } catch (error: any) {
      console.error('❌ Upload failed:', error)
      alert(`Upload failed: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploadingFiles([])
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    // Create new chat if none exists
    let chatId = currentChatId
    if (!chatId) {
      const newChat: ChatSession = {
        id: Date.now().toString(),
        title: generateChatTitle(input),
        messages: [],
        documents: [],
        createdAt: new Date().toISOString(),
        lastMessageAt: new Date().toISOString()
      }
      setChats([newChat, ...chats])
      setCurrentChatId(newChat.id)
      chatId = newChat.id
    }

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      activeDocuments: documents  // Track which documents were active
    }

    // Update chat with new message
    setChats(prevChats => prevChats.map(chat => {
      if (chat.id === chatId) {
        const updatedMessages = [...chat.messages, userMessage]
        return {
          ...chat,
          messages: updatedMessages,
          title: chat.messages.length === 0 ? generateChatTitle(input) : chat.title,
          lastMessageAt: new Date().toISOString()
        }
      }
      return chat
    }))

    setInput('')
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_URL}/query`, {
        question: input,
        conversation_id: chatId,
        top_k: 3
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.answer,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        sources: response.data.sources || []
      }

      setChats(prevChats => prevChats.map(chat => 
        chat.id === chatId 
          ? { ...chat, messages: [...chat.messages, assistantMessage] }
          : chat
      ))
    } catch (error: any) {
      console.error('Error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: `❌ Error: ${error.response?.data?.detail || 'Unable to get response. Make sure the API server is running.'}`,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }
      
      setChats(prevChats => prevChats.map(chat => 
        chat.id === chatId 
          ? { ...chat, messages: [...chat.messages, errorMessage] }
          : chat
      ))
    } finally {
      setIsLoading(false)
    }
  }

  const deleteChat = (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setChats(chats.filter(c => c.id !== chatId))
    if (currentChatId === chatId) {
      setCurrentChatId(chats.length > 1 ? chats.find(c => c.id !== chatId)?.id || null : null)
    }
  }

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  // Initialize with first chat
  useEffect(() => {
    if (chats.length === 0) {
      createNewChat()
    }
  }, [])

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ x: -300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="w-80 bg-slate-900/50 backdrop-blur-xl border-r border-slate-800 flex flex-col"
          >
            {/* Sidebar Header */}
            <div className="p-6 border-b border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-primary-400" />
                  Chat History
                </h2>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <Sidebar className="w-5 h-5 text-slate-400" />
                </button>
              </div>
              <button
                onClick={createNewChat}
                className="w-full py-3 px-4 bg-gradient-to-r from-primary-500 to-secondary-600 hover:from-primary-600 hover:to-secondary-700 rounded-lg text-sm font-medium text-white transition-all flex items-center justify-center gap-2 shadow-lg shadow-primary-500/20"
              >
                <Plus className="w-4 h-4" />
                New Chat
              </button>
            </div>

            {/* Chat List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {chats.map((chat) => (
                <motion.div
                  key={chat.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  onClick={() => setCurrentChatId(chat.id)}
                  className={`group relative p-4 rounded-lg cursor-pointer transition-all ${
                    currentChatId === chat.id
                      ? 'bg-primary-500/20 border-2 border-primary-500'
                      : 'bg-slate-800/30 border border-slate-700 hover:border-primary-500/50 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-200 truncate">{chat.title}</p>
                      <p className="text-xs text-slate-500 mt-1">
                        {chat.messages.length} messages
                        {chat.documents.length > 0 && ` • ${chat.documents.length} docs`}
                      </p>
                      {chat.documents.length > 0 && (
                        <div className="flex items-center gap-1 mt-2">
                          <FileText className="w-3 h-3 text-primary-400" />
                          <span className="text-xs text-primary-400">Has documents</span>
                        </div>
                      )}
                    </div>
                    <button
                      onClick={(e) => deleteChat(chat.id, e)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 rounded transition-all"
                    >
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Sidebar Footer */}
            <div className="p-6 border-t border-slate-800 space-y-3">
              <div className="bg-slate-800/50 rounded-lg p-3 space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Model</span>
                  <span className="text-slate-200 font-medium">Amazon Nova 2 Lite</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Embeddings</span>
                  <span className="text-slate-200 font-medium">Local (384-dim)</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Mode</span>
                  <span className="text-primary-400 font-medium">🧠 Reasoning Enabled</span>
                </div>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <motion.header
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="bg-gradient-to-r from-primary-600 to-secondary-600 p-6 shadow-2xl relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLW9wYWNpdHk9IjAuMDUiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-30" />
          <div className="relative flex items-center justify-between">
            <div className="flex items-center gap-4">
              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
                >
                  <Sidebar className="w-5 h-5 text-white" />
                </button>
              )}
              <div>
                <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                  <span className="text-4xl">🤖</span>
                  {currentChat?.title || 'RAG Chatbot'}
                </h1>
                <p className="text-white/90 text-sm mt-1">
                  {documents.length > 0 ? `📄 ${documents.length} documents loaded` : 'AI-powered with Amazon Nova reasoning'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-white text-sm font-medium">GPU Accelerated</span>
            </div>
          </div>
        </motion.header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-8 space-y-6">
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-3xl mx-auto text-center py-20"
            >
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                className="text-8xl mb-6"
              >
                🤖
              </motion.div>
              <h2 className="text-4xl font-bold text-slate-100 mb-4">Amazon Nova 2 Lite</h2>
              <p className="text-xl text-slate-400 mb-12">With advanced reasoning capabilities</p>
              
              <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto">
                {[
                  { icon: '🧠', text: 'How many r\'s in strawberry?' },
                  { icon: '💻', text: 'Write a Python function' },
                  { icon: '📊', text: 'Explain quantum computing' },
                  { icon: '🌍', text: 'Translate to Spanish' }
                ].map((item, idx) => (
                  <motion.button
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    whileHover={{ scale: 1.05, y: -5 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setInput(item.text)}
                    className="bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700 hover:border-primary-500 rounded-xl p-4 text-left transition-all group"
                  >
                    <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">{item.icon}</div>
                    <div className="text-sm text-slate-300">{item.text}</div>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          ) : (
            <>
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-2xl ${
                    message.role === 'user' 
                      ? 'bg-gradient-to-br from-primary-500 to-secondary-600' 
                      : 'bg-slate-800 border-2 border-slate-700'
                  }`}>
                    {message.role === 'user' ? '👤' : '🤖'}
                  </div>
                  
                  <div className={`flex-1 max-w-3xl ${message.role === 'user' ? 'flex justify-end' : ''}`}>
                    {/* Show active documents for user messages */}
                    {message.role === 'user' && message.activeDocuments && message.activeDocuments.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-2 justify-end">
                        {message.activeDocuments.map((doc, idx) => (
                          <motion.div
                            key={idx}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="flex items-center gap-1 bg-primary-500/20 border border-primary-500/40 rounded-full px-3 py-1"
                          >
                            <FileText className="w-3 h-3 text-primary-400" />
                            <span className="text-xs text-primary-300 font-medium">{doc}</span>
                          </motion.div>
                        ))}
                      </div>
                    )}
                    
                    <div className={`rounded-2xl p-4 ${
                      message.role === 'user'
                        ? 'bg-gradient-to-br from-primary-500 to-secondary-600 text-white rounded-br-sm'
                        : 'bg-slate-800/50 border border-slate-700 text-slate-100 rounded-bl-sm'
                    }`}>
                      <ReactMarkdown
                        className="prose prose-invert prose-sm max-w-none"
                        components={{
                          code({node, className, children, ...props}: any) {
                            const match = /language-(\w+)/.exec(className || '')
                            const inline = !match
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={vscDarkPlus}
                                language={match[1]}
                                PreTag="div"
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={`${className} bg-black/30 px-1.5 py-0.5 rounded`} {...props}>
                                {children}
                              </code>
                            )
                          }
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                      <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/10">
                        <span className="text-xs opacity-60">{message.timestamp}</span>
                        {message.role === 'assistant' && (
                          <button
                            onClick={() => copyToClipboard(message.content, index)}
                            className="p-1 hover:bg-white/10 rounded transition-colors"
                          >
                            {copiedIndex === index ? (
                              <CheckCircle className="w-4 h-4 text-green-400" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 space-y-2">
                        <p className="text-xs text-slate-400 font-medium">📄 Sources:</p>
                        {message.sources.map((source, idx) => (
                          <motion.div
                            key={idx}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            className="bg-slate-800/30 border border-slate-700 rounded-lg p-3 text-sm hover:border-primary-500 transition-colors"
                          >
                            <p className="text-slate-300 font-medium mb-1">{source.source}</p>
                            <p className="text-slate-500 text-xs line-clamp-2">{source.content_preview}</p>
                          </motion.div>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
              
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-4"
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-slate-800 border-2 border-slate-700 flex items-center justify-center text-2xl">
                    🤖
                  </div>
                  <div className="bg-slate-800/50 border border-slate-700 rounded-2xl rounded-bl-sm p-4">
                    <div className="flex gap-2">
                      {[0, 1, 2].map((i) => (
                        <motion.div
                          key={i}
                          animate={{ y: [0, -10, 0] }}
                          transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.2 }}
                          className="w-2 h-2 bg-primary-400 rounded-full"
                        />
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="p-6 border-t border-slate-800 bg-slate-900/50 backdrop-blur-xl">
          <div className="max-w-4xl mx-auto">
            {/* Uploading indicator */}
            {uploadingFiles.length > 0 && (
              <div className="mb-3 p-3 bg-primary-500/10 border border-primary-500/30 rounded-lg">
                <div className="flex items-center gap-2 text-sm text-primary-400">
                  <div className="animate-spin w-4 h-4 border-2 border-primary-400 border-t-transparent rounded-full" />
                  <span>Uploading {uploadingFiles.join(', ')}...</span>
                </div>
              </div>
            )}
            
            <div className="flex items-end gap-3 bg-slate-800/50 border border-slate-700 focus-within:border-primary-500 rounded-2xl p-3 transition-all">
              <input
                type="file"
                ref={fileInputRef}
                multiple
                accept=".pdf,.txt,.docx"
                onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
                className="hidden"
              />
              
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={!currentChatId || uploadingFiles.length > 0}
                className="flex-shrink-0 p-3 bg-slate-700 hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all group"
              >
                <Paperclip className="w-5 h-5 text-slate-300 group-hover:text-white group-hover:rotate-12 transition-all" />
              </button>
              
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                placeholder="Type your message... (📎 to attach files)"
                disabled={isLoading}
                className="flex-1 bg-transparent border-none outline-none text-slate-100 placeholder-slate-500 py-2 px-2"
              />
              
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                className="flex-shrink-0 p-3 bg-gradient-to-r from-primary-500 to-secondary-600 hover:from-primary-600 hover:to-secondary-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all shadow-lg shadow-primary-500/20 hover:shadow-primary-500/40 hover:scale-105"
              >
                <Send className="w-5 h-5 text-white" />
              </button>
            </div>
            
            <p className="text-center text-xs text-slate-500 mt-3">
              💡 Nova 2 Lite: Code, reasoning, 50+ languages • 📎 Upload docs for RAG mode
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
