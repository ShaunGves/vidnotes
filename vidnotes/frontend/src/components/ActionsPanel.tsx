import { clsx } from 'clsx'
import { CheckSquare, Lightbulb, RotateCcw, BookOpen } from 'lucide-react'
import type { ActionItem } from '../types'

const CATEGORY_CONFIG = {
  task: { icon: CheckSquare, color: 'text-accent', bg: 'bg-accent/10', label: 'Task' },
  decision: { icon: Lightbulb, color: 'text-warning', bg: 'bg-warning/10', label: 'Decision' },
  followup: { icon: RotateCcw, color: 'text-positive', bg: 'bg-positive/10', label: 'Follow-up' },
  resource: { icon: BookOpen, color: 'text-text-secondary', bg: 'bg-muted', label: 'Resource' },
}

const PRIORITY_BADGE = {
  high: 'bg-danger/15 text-danger',
  medium: 'bg-warning/15 text-warning',
  low: 'bg-positive/15 text-positive',
}

interface Props {
  actions: ActionItem[]
}

export function ActionsPanel({ actions }: Props) {
  const grouped = actions.reduce((acc, a) => {
    ;(acc[a.category] = acc[a.category] || []).push(a)
    return acc
  }, {} as Record<string, ActionItem[]>)

  if (actions.length === 0) {
    return (
      <div className="text-center py-16 text-text-muted">
        <CheckSquare size={32} className="mx-auto mb-3 opacity-40" />
        <p className="text-sm">No action items found in this video.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {(Object.keys(CATEGORY_CONFIG) as ActionItem['category'][])
        .filter((cat) => grouped[cat]?.length)
        .map((cat) => {
          const cfg = CATEGORY_CONFIG[cat]
          const Icon = cfg.icon
          return (
            <div key={cat}>
              <div className="flex items-center gap-2 mb-3">
                <span className={clsx('p-1.5 rounded-lg', cfg.bg)}>
                  <Icon size={14} className={cfg.color} />
                </span>
                <h3 className="text-sm font-semibold text-text-primary">{cfg.label}s</h3>
                <span className="text-xs text-text-muted bg-muted px-1.5 py-0.5 rounded">
                  {grouped[cat].length}
                </span>
              </div>
              <div className="space-y-2">
                {grouped[cat].map((item, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 bg-surface border border-border rounded-xl">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-text-primary">{item.text}</p>
                      {item.assignee && (
                        <p className="text-xs text-text-muted mt-1">→ {item.assignee}</p>
                      )}
                    </div>
                    <span className={clsx('text-xs px-2 py-0.5 rounded font-medium flex-shrink-0', PRIORITY_BADGE[item.priority])}>
                      {item.priority}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
    </div>
  )
}
