import { fmtLongDate } from '../lib/format'
import type { LoadState, ViewKey } from '../types'
import { StatusChip } from './StatusChip'

const TABS: { key: ViewKey; label: string }[] = [
  { key: 'overview', label: 'Overview' },
  { key: 'expirations', label: 'Expirations' },
  { key: 'pipeline', label: 'Pipeline' },
  { key: 'table', label: 'All Sites' },
]

interface HeaderProps {
  view: ViewKey
  onView: (v: ViewKey) => void
  state: LoadState
  onRefresh: () => void
  asOf: Date
}

export function Header({ view, onView, state, onRefresh, asOf }: HeaderProps) {
  return (
    <header className="hdr">
      <img className="hdr-logo" src="/assets/Cresa_Logo_Primary_wide.svg" alt="Cresa" />
      <div className="hdr-divider" />
      <div style={{ minWidth: 0 }}>
        <div className="hdr-title">Rimkus Real Estate Portfolio</div>
        <div className="hdr-sub">
          Occupier Portfolio Management · As of {fmtLongDate(asOf)}
        </div>
      </div>
      <div className="spacer" />
      <StatusChip state={state} onRefresh={onRefresh} />
      <div className="tabs" role="tablist" aria-label="Dashboard views">
        {TABS.map((t) => (
          <button
            key={t.key}
            className="tab"
            role="tab"
            aria-selected={view === t.key}
            onClick={() => onView(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>
    </header>
  )
}
