import { Clock } from 'lucide-react'
import type { Timestamp } from '../types'
import { formatTime } from '../utils/api'

interface Props {
  timestamps: Timestamp[]
}

export function TimestampsPanel({ timestamps }: Props) {
  return (
    <div className="space-y-2 animate-fade-in">
      {timestamps.map((ts, i) => (
        <div
          key={i}
          className="flex gap-3 p-3 bg-surface border border-border rounded-xl hover:border-accent/30 transition-colors group"
        >
          <div className="flex-shrink-0 flex items-center justify-center w-16">
            <span className="font-mono text-sm font-medium text-accent bg-accent/10 px-2 py-1 rounded-lg">
              {formatTime(ts.time)}
            </span>
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-text-primary">{ts.label}</p>
            <p className="text-xs text-text-secondary mt-0.5 leading-relaxed">{ts.summary}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
