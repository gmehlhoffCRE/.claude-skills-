import { fmtMoney, fmtSf } from '../../lib/format'
import type { Metrics } from '../../lib/metrics'
import { Card } from '../Card'

/** Rent & footprint by region: bar width is AGR relative to the largest region. */
export function RegionBars({ m }: { m: Metrics }) {
  return (
    <Card variant="pad" style={{ padding: '16px 18px' }}>
      <h2 className="card-title" style={{ marginBottom: 14 }}>
        Rent &amp; Footprint by Region
      </h2>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          flex: 1,
          gap: 12,
        }}
      >
        {m.regions.map((r) => (
          <div className="region-row" key={r.name}>
            <div style={{ minWidth: 0 }}>
              <div className="region-name">{r.name}</div>
              <div className="region-meta">
                {r.count} site{r.count === 1 ? '' : 's'} · {fmtSf(r.sf)} SF
              </div>
            </div>
            <div className="region-track">
              <div className="region-fill" style={{ width: `${r.barPct}%`, background: r.color }} />
            </div>
            <div style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
              <div className="region-agr">{fmtMoney(r.agr)}</div>
              <div className="region-psf">${r.psf.toFixed(2)} /SF</div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
