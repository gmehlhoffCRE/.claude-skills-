import { C } from '../tokens'
import { fmtMoney } from '../lib/format'
import type { LoadState } from '../types'

const SOURCE_LABEL: Record<string, string> = {
  'sheets-api': 'Google Sheets API',
  'sheets-csv': 'Google Sheets (published CSV)',
  fixture: 'local dev fixture',
  cache: 'last-good cached copy',
}

/**
 * Header data-source chip: green when the sheet answered, amber when we are serving
 * cached data after a failed fetch. Click re-fetches.
 */
export function StatusChip({ state, onRefresh }: { state: LoadState; onRefresh: () => void }) {
  if (state.status === 'loading') {
    return (
      <span className="chip-data" style={{ color: C.muted, cursor: 'default' }}>
        <span className="chip-dot" style={{ background: C.muted }} />
        LOADING SHEET…
      </span>
    )
  }

  if (state.status === 'error') {
    return (
      <button className="chip-data" style={{ color: C.danger }} onClick={onRefresh} title={state.error}>
        <span className="chip-dot" style={{ background: C.danger }} />
        NO DATA · RETRY
      </button>
    )
  }

  const { data } = state
  const stale = state.stale
  const totalAgr = data.leases.reduce((a, l) => a + l.agr, 0)
  const when = data.fetchedAt.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
  const title = [
    `Source: ${SOURCE_LABEL[data.source] ?? data.source}`,
    `Fetched ${data.fetchedAt.toLocaleString('en-US')}`,
    stale ? `Live fetch failed: ${state.error}` : null,
    ...data.warnings.slice(0, 5),
    data.warnings.length > 5 ? `…and ${data.warnings.length - 5} more warnings` : null,
    'Click to refresh.',
  ]
    .filter(Boolean)
    .join('\n')

  return (
    <button
      className="chip-data"
      onClick={onRefresh}
      title={title}
      style={stale ? { color: C.warn, borderColor: C.goldenrod } : undefined}
    >
      <span className="chip-dot" style={{ background: stale ? C.goldenrod : C.ok }} />
      {stale ? `CACHED ${when}` : 'LIVE'} · {data.leases.length} LEASES · {fmtMoney(totalAgr)} AGR
    </button>
  )
}
