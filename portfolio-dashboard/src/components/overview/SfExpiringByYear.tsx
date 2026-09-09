import { C } from '../../tokens'
import { fmtSf } from '../../lib/format'
import type { Metrics } from '../../lib/metrics'
import { Card } from '../Card'

/** Vertical bars, one per expiration year bucket; the overflow bucket is gold. */
export function SfExpiringByYear({ m }: { m: Metrics }) {
  const overflow = m.yearBuckets.find((b) => b.isOverflow)
  const biggestOverflow = overflow?.leases.slice().sort((a, b) => b.sf - a.sf)[0]

  const footnote = [
    biggestOverflow
      ? `${biggestOverflow.city} (${fmtSf(biggestOverflow.sf)} SF, ${
          biggestOverflow.expDate?.getUTCFullYear() ?? ''
        }) shown in gold`
      : null,
    m.mtmCount > 0
      ? `${m.mtmCount} lease${m.mtmCount === 1 ? '' : 's'} month-to-month`
      : null,
  ]
    .filter(Boolean)
    .join(' · ')

  return (
    <Card variant="pad" title="SF Expiring by Year">
      <div className="bars">
        {m.yearBuckets.map((b) => (
          <div className="bar-col" key={b.key}>
            <div className="bar-val">{b.sf > 0 ? fmtSf(b.sf) : '—'}</div>
            <div
              className="bar"
              style={{
                height: `${Math.max(3, Math.round((b.sf / m.maxYearSf) * 100))}%`,
                background: b.isOverflow ? C.goldenrod : C.midnight,
              }}
            />
          </div>
        ))}
      </div>
      <div className="bar-axis">
        {m.yearBuckets.map((b) => (
          <div key={b.key}>{b.label}</div>
        ))}
      </div>
      {footnote && <div className="footnote">{footnote}</div>}
    </Card>
  )
}
