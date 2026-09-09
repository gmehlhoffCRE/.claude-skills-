import { useMemo, useState } from 'react'
import { config } from './config'
import { usePortfolioData } from './hooks/usePortfolioData'
import { buildMetrics, utcToday } from './lib/metrics'
import type { ViewKey } from './types'
import { ErrorPanel } from './components/ErrorPanel'
import { Header } from './components/Header'
import { KpiBand } from './components/KpiBand'
import { LoadingSkeleton } from './components/LoadingSkeleton'
import { AllSitesView } from './components/views/AllSitesView'
import { ExpirationsView } from './components/views/ExpirationsView'
import { OverviewView } from './components/views/OverviewView'
import { PipelineView } from './components/views/PipelineView'

export default function App() {
  // View state lives here so switching tabs preserves each view's own filters.
  const [view, setView] = useState<ViewKey>('overview')
  const { state, refresh } = usePortfolioData()
  const asOf = useMemo(() => utcToday(), [])

  const metrics = useMemo(() => {
    if (state.status !== 'ready') return null
    return buildMetrics(state.data.leases, {
      asOf,
      expiringMonths: config.expiringMonths,
      runwayMonths: config.runwayMonths,
    })
  }, [state, asOf])

  return (
    <div className="app">
      <Header view={view} onView={setView} state={state} onRefresh={refresh} asOf={asOf} />

      {state.status === 'loading' && <LoadingSkeleton />}
      {state.status === 'error' && <ErrorPanel error={state.error} onRetry={refresh} />}

      {metrics && (
        <>
          <KpiBand m={metrics} />
          {view === 'overview' && <OverviewView m={metrics} />}
          {view === 'expirations' && <ExpirationsView m={metrics} />}
          {view === 'pipeline' && <PipelineView m={metrics} />}
          {view === 'table' && <AllSitesView m={metrics} />}
        </>
      )}

      <div className="spacer" />
      <footer className="foot">
        <span>
          Source: {config.sourceLabel}
          {metrics ? ` · ${metrics.leases.length} leases` : ''}
        </span>
        <span>
          Headcount by site not yet in source data — add a column to enable cost-per-seat
        </span>
      </footer>
    </div>
  )
}
