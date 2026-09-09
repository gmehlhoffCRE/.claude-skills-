import { fmtInt, fmtMoney } from '../../lib/format'
import type { Metrics } from '../../lib/metrics'
import { Card } from '../Card'

/** Leases whose Cresa note mentions a closing or a sublease. */
export function NeedsAttention({ m }: { m: Metrics }) {
  return (
    <Card variant="pad">
      <h2 className="card-title" style={{ marginBottom: 8 }}>
        Needs Attention
      </h2>
      {m.attention.length === 0 && (
        <div className="card-hint">No leases flagged in Cresa notes.</div>
      )}
      {m.attention.map(({ lease, flag }) => (
        <div className="attn-row" key={lease.id}>
          <span className={`chip ${flag === 'CLOSING' ? 'chip-closing' : 'chip-sublease'}`}>
            {flag}
          </span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="attn-city">
              {lease.city}
              {lease.st ? `, ${lease.st}` : ''}{' '}
              <span className="attn-meta">
                · {fmtInt(lease.sf)} SF · {fmtMoney(lease.agr)}
              </span>
            </div>
            <div className="attn-note">{lease.note}</div>
          </div>
        </div>
      ))}
    </Card>
  )
}
