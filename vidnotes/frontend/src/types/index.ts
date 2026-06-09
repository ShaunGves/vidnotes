export type JobStatus = 'pending' | 'downloading' | 'transcribing' | 'processing' | 'done' | 'failed'

export interface Timestamp {
  time: number
  label: string
  summary: string
}

export interface ActionItem {
  text: string
  category: 'task' | 'decision' | 'followup' | 'resource'
  priority: 'high' | 'medium' | 'low'
  assignee?: string | null
}

export interface NoteSection {
  heading: string
  content: string
  start_time?: number
  end_time?: number
}

export interface JobResult {
  notes: NoteSection[]
  timestamps: Timestamp[]
  action_items: ActionItem[]
  summary: string
  transcript: string
}

export interface Job {
  id: string
  status: JobStatus
  progress: number
  stage: string
  title?: string
  duration?: number
  created_at: string
  result?: JobResult
  error?: string
}

export interface QueryResponse {
  answer: string
  sources: Array<{
    text: string
    start: number
    end: number
    score: number
  }>
}
