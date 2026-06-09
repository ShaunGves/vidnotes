import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User } from 'lucide-react'
import { api, formatTime } from '../utils/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{ text: string; start: number; end: number; score: number }>
}

interface Props {
  jobId: string
}

export function ChatPanel({ jobId }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Ask me anything about this video. I\'ll search the transcript to answer accurately.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    const q = input.trim()
    if (!q || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: q }])
    setLoading(true)
    try {
      const res = await api.query(jobId, q)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.answer,
        sources: res.sources,
      }])
    } catch (e: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${e.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[520px] animate-fade-in">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 mb-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center ${
              msg.role === 'assistant' ? 'bg-accent/20' : 'bg-muted'
            }`}>
              {msg.role === 'assistant' ? <Bot size={14} className="text-accent" /> : <User size={14} className="text-text-secondary" />}
            </div>
            <div className={`max-w-[80%] space-y-1 ${msg.role === 'user' ? 'items-end' : ''}`}>
              <div className={`rounded-xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === 'assistant'
                  ? 'bg-surface border border-border text-text-primary'
                  : 'bg-accent text-white'
              }`}>
                {msg.content}
              </div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="space-y-1 pt-1">
                  <p className="text-xs text-text-muted px-1">Sources from transcript:</p>
                  {msg.sources.slice(0, 2).map((src, j) => (
                    <div key={j} className="bg-muted/50 rounded-lg px-3 py-2 text-xs text-text-secondary border border-border">
                      <span className="text-accent font-mono">{formatTime(src.start)}</span>
                      {' — '}
                      {src.text.slice(0, 120)}...
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-lg bg-accent/20 flex items-center justify-center">
              <Bot size={14} className="text-accent" />
            </div>
            <div className="bg-surface border border-border rounded-xl px-4 py-3">
              <div className="flex gap-1 items-center h-4">
                {[0, 1, 2].map(i => (
                  <span key={i} className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce" style={{ animationDelay: `${i * 150}ms` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="What were the key decisions made?"
          className="flex-1 bg-canvas border border-border rounded-xl px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
        />
        <button
          onClick={send}
          disabled={!input.trim() || loading}
          className="bg-accent hover:bg-accent-bright disabled:opacity-40 text-white p-2.5 rounded-xl transition-colors"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
