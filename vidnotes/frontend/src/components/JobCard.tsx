import { clsx } from 'clsx'
import { CheckCircle2, AlertCircle, Loader2, Clock } from 'lucide-react'
import type { Job } from '../types'
import { ProgressBar } from './ProgressBar'

interface Props {
  job: Job
  onClick: () => void
  active?: boolean
}

const STATUS_ICON = {
  done: <CheckCircle2 size={14} className="text-positive" />,
  failed: <AlertCircle size={14} className="text-danger" />,
  pending: <Clock size={14} className="text-text-muted" />,
  downloading: <Loader2 size={14} className="text-accent animate-spin" />,
  transcribing: <Loader2 size={14} className="text-accent animate-spin" />,
  processing: <Loader2 size={14} className="text-accent animate-spin" />,
}

export function JobCard({ job, onClick, active }: Props) {
  const isProcessing = !['done', 'failed'].includes(job.status)
  const date = new Date(job.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })

  return (
    <button
      onClick={onClick}
      className={clsx(
        'w-full text-left p-4 rounded-xl border transition-all',
        active
          ? 'border-accent bg-accent/10'
          : 'border-border bg-surface hover:border-muted hover:bg-muted/20'
      )}
    >
      <div className="flex items-start gap-2">
        <span className="mt-0.5 flex-shrink-0">{STATUS_ICON[job.status]}</span>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-text-primary truncate">{job.title || 'Untitled'}</p>
          <p className="text-xs text-text-muted mt-0.5">{date}</p>
          {isProcessing && (
            <div className="mt-2">
              <ProgressBar progress={job.progress} status={job.status} stage={job.stage} />
            </div>
          )}
          {job.status === 'failed' && (
            <p className="text-xs text-danger mt-1 truncate">{job.error}</p>
          )}
        </div>
      </div>
    </button>
  )
}
