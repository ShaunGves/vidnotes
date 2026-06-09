import { useState, useEffect, useCallback, useRef } from 'react'
import { api, createJobSocket } from '../utils/api'
import type { Job } from '../types'

export function useJob(jobId: string | null) {
  const [job, setJob] = useState<Job | null>(null)
  const [loading, setLoading] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  const fetchJob = useCallback(async (id: string) => {
    try {
      const data = await api.getJob(id)
      setJob(data)
      return data
    } catch (e) {
      console.error(e)
      return null
    }
  }, [])

  useEffect(() => {
    if (!jobId) return
    setLoading(true)
    fetchJob(jobId).then(() => setLoading(false))

    // Connect WebSocket for live progress
    const ws = createJobSocket(jobId, (update) => {
      setJob((prev) => prev ? {
        ...prev,
        status: update.status as Job['status'],
        progress: update.progress,
        stage: update.stage,
        error: update.error,
      } : null)

      // If done/failed, fetch the full result
      if (update.status === 'done' || update.status === 'failed') {
        fetchJob(jobId)
        ws.close()
      }
    })
    wsRef.current = ws

    return () => {
      ws.close()
    }
  }, [jobId, fetchJob])

  return { job, loading, refetch: () => jobId && fetchJob(jobId) }
}
