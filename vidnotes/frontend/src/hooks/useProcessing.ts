import { useCallback } from 'react'
import { useStore } from '@/store'
import { ingestURL, ingestFile, createSSEStream } from '@/utils/api'

export function useProcessing() {
  const { setJob, setStatus, setResult, setError } = useStore()

  const startStream = useCallback((jobId: string) => {
    const es = createSSEStream(jobId)

    es.onmessage = (e) => {
      const data = JSON.parse(e.data)
      setStatus(data.status, data.progress, data.stage_message)
      if (data.status === 'done' && data.result) {
        setResult(data.result)
        es.close()
      }
      if (data.status === 'error') {
        setError(data.error || 'Unknown error')
        es.close()
      }
    }

    es.onerror = () => {
      setError('Connection lost. Please refresh.')
      es.close()
    }

    return () => es.close()
  }, [setStatus, setResult, setError])

  const submitURL = useCallback(async (url: string) => {
    try {
      const { job_id } = await ingestURL(url)
      setJob(job_id)
      startStream(job_id)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to submit URL')
    }
  }, [setJob, setError, startStream])

  const submitFile = useCallback(async (file: File) => {
    try {
      const { job_id } = await ingestFile(file)
      setJob(job_id)
      startStream(job_id)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to upload file')
    }
  }, [setJob, setError, startStream])

  return { submitURL, submitFile }
}
