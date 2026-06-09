import { useState, useEffect } from 'react'
import { FileText, Clock, CheckSquare, MessageSquare, Download, Trash2, Zap, ChevronRight } from 'lucide-react'
import { clsx } from 'clsx'
import { SubmitForm } from '../components/SubmitForm'
import { JobCard } from '../components/JobCard'
import { NotesPanel } from '../components/NotesPanel'
import { TimestampsPanel } from '../components/TimestampsPanel'
import { ActionsPanel } from '../components/ActionsPanel'
import { ChatPanel } from '../components/ChatPanel'
import { ProgressBar } from '../components/ProgressBar'
import { useJob } from '../hooks/useJob'
import { api } from '../utils/api'
import type { Job } from '../types'

type Tab = 'notes' | 'timestamps' | 'actions' | 'chat'

const TABS: { id: Tab; icon: typeof FileText; label: string }[] = [
  { id: 'notes', icon: FileText, label: 'Notes' },
  { id: 'timestamps', icon: Clock, label: 'Timestamps' },
  { id: 'actions', icon: CheckSquare, label: 'Actions' },
  { id: 'chat', icon: MessageSquare, label: 'Ask' },
]

function ResultView({ jobId }: { jobId: string }) {
  const { job } = useJob(jobId)
  const [tab, setTab] = useState<Tab>('notes')

  if (!job) return null

  const isProcessing = !['done', 'failed'].includes(job.status)
  const result = job.result

  const downloadMarkdown = async () => {
    const md = await api.exportMarkdown(jobId)
    const blob = new Blob([md], { type: 'text/markdown' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${job.title || 'vidnotes'}.md`
    a.click()
  }

  return (
    <div className="flex flex-col h-full animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-5">
        <div className="min-w-0">
          <h2 className="font-bold text-text-primary truncate">{job.title || 'Untitled'}</h2>
          <p className="text-xs text-text-muted mt-0.5">
            {job.status === 'done' && result && (
              <>
                {result.notes.length} sections · {result.timestamps.length} timestamps · {result.action_items.length} actions
              </>
            )}
          </p>
        </div>
        {job.status === 'done' && (
          <button
            onClick={downloadMarkdown}
            className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-text-primary border border-border hover:border-accent/50 rounded-lg px-3 py-1.5 transition-all flex-shrink-0"
          >
            <Download size={13} />
            Export
          </button>
        )}
      </div>

      {/* Processing state */}
      {isProcessing && (
        <div className="flex-1 flex flex-col items-center justify-center">
          <div className="w-full max-w-sm space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-accent/20 flex items-center justify-center mx-auto">
              <Zap size={22} className="text-accent animate-pulse" />
            </div>
            <ProgressBar progress={job.progress} status={job.status} stage={job.stage} />
            <p className="text-xs text-text-muted text-center">This can take a few minutes for longer videos</p>
          </div>
        </div>
      )}

      {/* Failed state */}
      {job.status === 'failed' && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-2">
            <p className="text-danger font-medium">Processing failed</p>
            <p className="text-xs text-text-muted">{job.error}</p>
          </div>
        </div>
      )}

      {/* Results */}
      {job.status === 'done' && result && (
        <>
          <div className="flex gap-1 mb-5 bg-canvas rounded-xl p-1 border border-border">
            {TABS.map(({ id, icon: Icon, label }) => (
              <button
                key={id}
                onClick={() => setTab(id)}
                className={clsx(
                  'flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-all',
                  tab === id
                    ? 'bg-accent text-white shadow-sm'
                    : 'text-text-secondary hover:text-text-primary'
                )}
              >
                <Icon size={13} />
                {label}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto">
            {tab === 'notes' && <NotesPanel summary={result.summary} sections={result.notes} />}
            {tab === 'timestamps' && <TimestampsPanel timestamps={result.timestamps} />}
            {tab === 'actions' && <ActionsPanel actions={result.action_items} />}
            {tab === 'chat' && <ChatPanel jobId={jobId} />}
          </div>
        </>
      )}
    </div>
  )
}

export function App() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    api.listJobs().then(setJobs).catch(() => {})
  }, [])

  const handleJobCreated = (job: Job) => {
    setJobs(prev => [job, ...prev])
    setSelectedId(job.id)
  }

  const deleteJob = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    await api.deleteJob(id)
    setJobs(prev => prev.filter(j => j.id !== id))
    if (selectedId === id) setSelectedId(null)
  }

  return (
    <div className="min-h-screen bg-canvas text-text-primary flex flex-col">
      {/* Top nav */}
      <header className="h-14 border-b border-border flex items-center px-5 gap-4 flex-shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-accent rounded-lg flex items-center justify-center">
            <Zap size={15} className="text-white" />
          </div>
          <span className="font-bold text-text-primary tracking-tight">VidNotes</span>
        </div>
        <span className="text-xs text-text-muted bg-muted px-2 py-0.5 rounded font-mono">v1.0</span>
        <div className="flex-1" />
        <span className="text-xs text-text-muted hidden sm:block">
          Whisper · Claude · ChromaDB
        </span>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className={clsx(
          'border-r border-border flex-shrink-0 flex flex-col transition-all duration-300',
          sidebarOpen ? 'w-72' : 'w-0 overflow-hidden'
        )}>
          <div className="p-4 flex-1 overflow-y-auto space-y-3">
            <SubmitForm onJobCreated={handleJobCreated} />

            {jobs.length > 0 && (
              <div className="space-y-1.5">
                <p className="text-xs text-text-muted uppercase tracking-wider font-medium px-1 pt-2">
                  Recent Jobs
                </p>
                {jobs.map(job => (
                  <div key={job.id} className="relative group">
                    <JobCard
                      job={job}
                      active={job.id === selectedId}
                      onClick={() => setSelectedId(job.id)}
                    />
                    <button
                      onClick={(e) => deleteJob(job.id, e)}
                      className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity text-text-muted hover:text-danger"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>

        {/* Toggle sidebar */}
        <button
          onClick={() => setSidebarOpen(v => !v)}
          className="self-center w-4 h-8 flex items-center justify-center text-text-muted hover:text-text-secondary transition-colors border-y border-r border-border rounded-r bg-surface"
        >
          <ChevronRight size={12} className={clsx('transition-transform', sidebarOpen && 'rotate-180')} />
        </button>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto">
          {selectedId ? (
            <div className="max-w-3xl mx-auto p-6 h-full">
              <ResultView jobId={selectedId} />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-center p-8">
              <div className="max-w-sm space-y-4">
                <div className="w-16 h-16 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto border border-accent/20">
                  <Zap size={28} className="text-accent" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-text-primary">Video → Structured Notes</h1>
                  <p className="text-sm text-text-secondary mt-2 leading-relaxed">
                    Paste a YouTube URL or upload a recording.<br />
                    Get notes, timestamps, and action items in minutes.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 justify-center">
                  {['YouTube lectures', 'Team meetings', 'Podcasts', 'Conference talks'].map(t => (
                    <span key={t} className="text-xs bg-surface border border-border text-text-muted px-2.5 py-1 rounded-lg">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
