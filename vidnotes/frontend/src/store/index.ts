import { create } from 'zustand'

export interface Timestamp {
  time: string
  seconds: number
  label: string
  summary: string
}

export interface ActionItem {
  task: string
  priority: 'high' | 'medium' | 'low'
  owner?: string | null
  context?: string | null
}

export interface NoteSection {
  heading: string
  bullets: string[]
}

export interface AnalysisResult {
  title: string
  overview: string
  sections: NoteSection[]
  timestamps: Timestamp[]
  action_items: ActionItem[]
  raw_transcript?: string
}

export type JobStatus = 'idle' | 'queued' | 'transcribing' | 'analyzing' | 'done' | 'error'

interface AppState {
  jobId: string | null
  status: JobStatus
  progress: number
  stageMessage: string
  result: AnalysisResult | null
  error: string | null
  activeTab: 'notes' | 'timestamps' | 'actions' | 'chat'
  chatHistory: { role: 'user' | 'assistant'; content: string }[]

  setJob: (id: string) => void
  setStatus: (s: JobStatus, progress: number, msg: string) => void
  setResult: (r: AnalysisResult) => void
  setError: (e: string) => void
  setActiveTab: (t: AppState['activeTab']) => void
  addChatMessage: (role: 'user' | 'assistant', content: string) => void
  reset: () => void
}

export const useStore = create<AppState>((set) => ({
  jobId: null,
  status: 'idle',
  progress: 0,
  stageMessage: '',
  result: null,
  error: null,
  activeTab: 'notes',
  chatHistory: [],

  setJob: (id) => set({ jobId: id, status: 'queued', progress: 0 }),
  setStatus: (status, progress, stageMessage) => set({ status, progress, stageMessage }),
  setResult: (result) => set({ result, status: 'done', progress: 100 }),
  setError: (error) => set({ error, status: 'error' }),
  setActiveTab: (activeTab) => set({ activeTab }),
  addChatMessage: (role, content) =>
    set((s) => ({ chatHistory: [...s.chatHistory, { role, content }] })),
  reset: () =>
    set({
      jobId: null, status: 'idle', progress: 0, stageMessage: '',
      result: null, error: null, chatHistory: [], activeTab: 'notes',
    }),
}))
