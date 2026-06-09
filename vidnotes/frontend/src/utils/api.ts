import type { Job, QueryResponse } from '../types'

const BASE = '/api/v1'

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  submitUrl: (url: string, title?: string) =>
    fetchJSON<Job>(`${BASE}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, title }),
    }),

  uploadFile: (file: File, title?: string) => {
    const form = new FormData()
    form.append('file', file)
    if (title) form.append('title', title)
    return fetchJSON<Job>(`${BASE}/jobs/upload`, { method: 'POST', body: form })
  },

  getJob: (id: string) => fetchJSON<Job>(`${BASE}/jobs/${id}`),

  listJobs: () => fetchJSON<Job[]>(`${BASE}/jobs`),

  query: (id: string, question: string) =>
    fetchJSON<QueryResponse>(`${BASE}/jobs/${id}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    }),

  exportMarkdown: async (id: string): Promise<string> => {
    const res = await fetch(`${BASE}/jobs/${id}/export?format=md`)
    if (!res.ok) throw new Error('Export failed')
    return res.text()
  },

  deleteJob: (id: string) =>
    fetchJSON(`${BASE}/jobs/${id}`, { method: 'DELETE' }),
}

export function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  return `${m}:${s.toString().padStart(2, '0')}`
}

export function createJobSocket(
  jobId: string,
  onMessage: (data: { status: string; progress: number; stage: string; error?: string }) => void
): WebSocket {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws/jobs/${jobId}`)
  ws.onmessage = (e) => {
    try { onMessage(JSON.parse(e.data)) } catch {}
  }
  return ws
}
