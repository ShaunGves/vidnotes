import { useState, useRef } from 'react'
import { Link2, Upload, Youtube, FileAudio } from 'lucide-react'
import { api } from '../utils/api'
import type { Job } from '../types'
import { clsx } from 'clsx'

interface Props {
  onJobCreated: (job: Job) => void
}

export function SubmitForm({ onJobCreated }: Props) {
  const [tab, setTab] = useState<'url' | 'upload'>('url')
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async () => {
    setError('')
    if (tab === 'url' && !url.trim()) { setError('Enter a video URL'); return }
    if (tab === 'upload' && !file) { setError('Select a file'); return }
    setLoading(true)
    try {
      const job = tab === 'url'
        ? await api.submitUrl(url.trim(), title || undefined)
        : await api.uploadFile(file!, title || undefined)
      onJobCreated(job)
      setUrl('')
      setTitle('')
      setFile(null)
    } catch (e: any) {
      setError(e.message || 'Failed to submit')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-surface border border-border rounded-2xl overflow-hidden animate-fade-in">
      {/* Tabs */}
      <div className="flex border-b border-border">
        {(['url', 'upload'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={clsx(
              'flex-1 py-3.5 text-sm font-medium flex items-center justify-center gap-2 transition-colors',
              tab === t
                ? 'text-accent border-b-2 border-accent -mb-px bg-accent/5'
                : 'text-text-secondary hover:text-text-primary'
            )}
          >
            {t === 'url' ? <Link2 size={15} /> : <Upload size={15} />}
            {t === 'url' ? 'Video URL' : 'Upload File'}
          </button>
        ))}
      </div>

      <div className="p-6 space-y-4">
        {tab === 'url' ? (
          <div className="space-y-1">
            <label className="text-xs text-text-secondary font-medium uppercase tracking-wider">
              YouTube / Video URL
            </label>
            <div className="relative">
              <Youtube size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-muted" />
              <input
                type="url"
                value={url}
                onChange={e => setUrl(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full bg-canvas border border-border rounded-xl pl-10 pr-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
              />
            </div>
          </div>
        ) : (
          <div
            onClick={() => fileRef.current?.click()}
            className="border-2 border-dashed border-border rounded-xl p-8 flex flex-col items-center gap-3 cursor-pointer hover:border-accent/50 hover:bg-accent/5 transition-all"
          >
            <FileAudio size={32} className="text-text-muted" />
            {file ? (
              <div className="text-center">
                <p className="text-sm font-medium text-text-primary">{file.name}</p>
                <p className="text-xs text-text-muted mt-1">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-sm text-text-secondary">Drop a video or audio file here</p>
                <p className="text-xs text-text-muted mt-1">mp4, mp3, wav, m4a • max 500MB</p>
              </div>
            )}
            <input
              ref={fileRef}
              type="file"
              accept="video/*,audio/*"
              className="hidden"
              onChange={e => setFile(e.target.files?.[0] || null)}
            />
          </div>
        )}

        <div className="space-y-1">
          <label className="text-xs text-text-secondary font-medium uppercase tracking-wider">
            Title (optional)
          </label>
          <input
            type="text"
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="e.g. CS Lecture 7 — Transformers"
            className="w-full bg-canvas border border-border rounded-xl px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
          />
        </div>

        {error && (
          <p className="text-danger text-sm flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-danger rounded-full" />
            {error}
          </p>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-accent hover:bg-accent-bright disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-all text-sm"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Submitting...
            </span>
          ) : 'Process Video →'}
        </button>
      </div>
    </div>
  )
}
