import { fmtMoney, fmtSf } from '../lib/format'
import type { Metrics } from '../lib/metrics'

interface Kpi {
  val: string
  label: string
  sub: string
}

/** Six KPIs, every one computed from the fetched rows. */
export function KpiBand({ m }: { m: Metrics }) {
  const n = m.leases.length
  const soonSf = m.expiringSoon.reduce((a, l) => a + l.sf, 0)
  const soonAgr = m.expiringSoon.reduce((a, l) => a + l.agr, 0)

  const kpis: Kpi[] = [
    {
      val: String(n),
      label: 'Locations',
      sub: `${m.regionCount} region${m.regionCount === 1 ? '' : 's'} · ${m.marketCount} markets`,
    },
    {
      val: `${fmtSf(m.totalSf)} SF`,
      label: 'Total Footprint',
      sub: `avg ${fmtSf(n ? m.totalSf / n : 0)} SF / site`,
    },
    { val: fmtMoney(m.totalAgr), label: 'Annual Gross Rent', sub: 'USD, all leases' },
    { val: `$${m.blendedPsf.toFixed(2)}`, label: 'Avg Rent / SF', sub: 'portfolio blended' },
    {
      val: String(m.expiringSoon.length),
      label: `Expiring ≤ ${m.expiringMonths} mo`,
      sub: `${fmtSf(soonSf)} SF · ${fmtMoney(soonAgr)}`,
    },
    {
      val: String(m.active.length),
      label: 'Active Transactions',
      sub: 'renewals, relos, subleases',
    },
  ]

  return (
    <div className="kpi-band">
      {kpis.map((k) => (
        <div className="kpi" key={k.label}>
          <div className="kpi-val">{k.val}</div>
          <div className="kpi-label">{k.label}</div>
          <div className="kpi-sub">{k.sub}</div>
        </div>
      ))}
    </div>
  )
}
