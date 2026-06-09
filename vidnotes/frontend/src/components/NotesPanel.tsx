import ReactMarkdown from 'react-markdown'
import type { NoteSection } from '../types'
import { formatTime } from '../utils/api'

interface Props {
  summary: string
  sections: NoteSection[]
}

export function NotesPanel({ summary, sections }: Props) {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Summary card */}
      <div className="bg-accent/10 border border-accent/20 rounded-xl p-4">
        <p className="text-xs text-accent font-semibold uppercase tracking-wider mb-2">Summary</p>
        <p className="text-sm text-text-primary leading-relaxed">{summary}</p>
      </div>

      {/* Note sections */}
      {sections.map((sec, i) => (
        <div key={i} className="bg-surface border border-border rounded-xl overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <h3 className="font-semibold text-text-primary text-sm">{sec.heading}</h3>
            {sec.start_time != null && (
              <span className="text-xs font-mono text-text-muted bg-muted px-2 py-0.5 rounded">
                {formatTime(sec.start_time)}
              </span>
            )}
          </div>
          <div className="px-4 py-3 prose prose-invert prose-sm max-w-none
            prose-p:text-text-secondary prose-li:text-text-secondary
            prose-strong:text-text-primary prose-code:text-accent-bright
            prose-code:bg-muted prose-code:px-1 prose-code:rounded
            prose-headings:text-text-primary">
            <ReactMarkdown>{sec.content}</ReactMarkdown>
          </div>
        </div>
      ))}
    </div>
  )
}
