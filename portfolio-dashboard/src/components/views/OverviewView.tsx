import { fmtMoney, fmtSf } from '../../lib/format'
import type { Metrics } from '../../lib/metrics'
import { Card } from '../Card'
import { DonutCard } from '../overview/DonutCard'
import { LargestCommitments } from '../overview/LargestCommitments'
import { NeedsAttention } from '../overview/NeedsAttention'
import { RegionBars } from '../overview/RegionBars'
import { SfExpiringByYear } from '../overview/SfExpiringByYear'
import { WorldMap } from '../overview/WorldMap'

export function OverviewView({ m }: { m: Metrics }) {
  const unmapped = m.leases.filter((l) => l.lat === null || l.lng === null).length

  return (
    <div className="view" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div className="ov-grid">
        <Card
          title="Global Footprint"
          hint={
            unmapped
              ? `dot size = SF · gold ring = active transaction · ${unmapped} site${
                  unmapped === 1 ? '' : 's'
                } missing LAT/LNG`
              : 'dot size = SF · gold ring = active transaction · click a dot for detail'
          }
          bodyStyle={{ flex: 1 }}
        >
          <WorldMap leases={m.leases} />
        </Card>
        <div className="ov-rail">
          <SfExpiringByYear m={m} />
          <DonutCard
            segments={m.segments}
            propertyTypes={m.propertyTypes}
            totalAgrLabel={fmtMoney(m.totalAgr)}
            totalSfLabel={`${fmtSf(m.totalSf)} SF`}
            fmtMoney={fmtMoney}
            fmtSf={fmtSf}
          />
        </div>
      </div>

      <div className="ov-grid">
        <div className="ov-inner">
          <RegionBars m={m} />
          <LargestCommitments m={m} />
        </div>
        <NeedsAttention m={m} />
      </div>
    </div>
  )
}
