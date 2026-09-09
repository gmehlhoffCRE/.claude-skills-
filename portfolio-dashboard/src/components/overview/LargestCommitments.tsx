import { fmtDate, fmtInt, fmtMoney } from '../../lib/format'
import type { Metrics } from '../../lib/metrics'
import { Card } from '../Card'

/** Top five leases by annual gross rent. */
export function LargestCommitments({ m }: { m: Metrics }) {
  return (
    <Card variant="pad" style={{ padding: '16px 18px' }}>
      <h2 className="card-title" style={{ marginBottom: 6 }}>
        Largest Commitments
      </h2>
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', flex: 1 }}>
        {m.top5.map((l, i) => (
          <div className="commit-row" key={l.id}>
            <div className="rank">{i + 1}</div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div className="commit-city">
                {l.city}
                {l.st ? `, ${l.st}` : ''}
              </div>
              <div className="commit-meta">
                {[l.addr, l.seg, `${fmtInt(l.sf)} SF`].filter(Boolean).join(' · ')}
              </div>
            </div>
            <div style={{ textAlign: 'right', flexShrink: 0 }}>
              <div style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--midnight)' }}>
                {fmtMoney(l.agr)}
              </div>
              <div style={{ fontSize: 10.5, color: 'var(--muted)' }}>{fmtDate(l.expDate)}</div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
