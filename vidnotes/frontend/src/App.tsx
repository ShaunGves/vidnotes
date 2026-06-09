import { useStore } from '@/store'
import LandingPage from '@/pages/LandingPage'
import ProcessingPage from '@/pages/ProcessingPage'
import ResultsPage from '@/pages/ResultsPage'

export default function App() {
  const { status } = useStore()

  if (status === 'idle') return <LandingPage />
  if (status === 'done') return <ResultsPage />
  return <ProcessingPage />
}
