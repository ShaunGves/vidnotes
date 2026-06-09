import { clsx } from 'clsx'
import type { JobStatus } from '../types'

const STATUS_COLOR: Record<JobStatus, string> = {
  pending: 'bg-text-muted',
  downloading: 'bg-accent',
  transcribing: 'bg-accent',
  processing: 'bg-accent-bright',
  done: 'bg-positive',
  failed: 'bg-danger',
}

interface Props {
  progress: number
  status: JobStatus
  stage: string
}

export function ProgressBar({ progress, status, stage }: Props) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-text-secondary font-medium">{stage}</span>
        <span className="text-text-muted font-mono">{progress}%</span>
      </div>
      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all duration-700 ease-out', STATUS_COLOR[status])}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}
