import { conicGradient, type Slice } from '../../lib/metrics'
import { Card } from '../Card'

interface DonutProps {
  title: string
  slices: Slice[]
  total: string
  totalCaption: string
  formatValue: (s: Slice) => string
}

function Donut({ title, slices, total, totalCaption, formatValue }: DonutProps) {
  return (
    <div style={{ minWidth: 0 }}>
      <h3 className="card-title">{title}</h3>
      <div className="donut" style={{ background: conicGradient(slices) }} role="img" aria-label={title}>
        <div className="donut-hole">
          <div className="donut-total">{total}</div>
          <div className="donut-cap">{totalCaption}</div>
        </div>
      </div>
      <div className="legend-list">
        {slices.map((s) => (
          <div className="legend-row" key={s.name}>
            <span className="legend-sw" style={{ background: s.color }} />
            <span className="legend-name">{s.name}</span>
            <span className="legend-val">{formatValue(s)}</span>
            <span className="legend-pct">{Math.round(s.share * 100)}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

interface DonutCardProps {
  segments: Slice[]
  propertyTypes: Slice[]
  totalAgrLabel: string
  totalSfLabel: string
  fmtMoney: (n: number) => string
  fmtSf: (n: number) => string
}

/** Two donuts side by side: AGR by operating segment, SF by property type. */
export function DonutCard({
  segments,
  propertyTypes,
  totalAgrLabel,
  totalSfLabel,
  fmtMoney,
  fmtSf,
}: DonutCardProps) {
  return (
    <Card variant="pad" style={{ flex: 1 }}>
      <div className="donuts">
        <Donut
          title="Annual Rent by Segment"
          slices={segments}
          total={totalAgrLabel}
          totalCaption="TOTAL AGR"
          formatValue={(s) => fmtMoney(s.value)}
        />
        <Donut
          title="SF by Property Type"
          slices={propertyTypes}
          total={totalSfLabel}
          totalCaption="TOTAL SF"
          formatValue={(s) => `${fmtSf(s.value)} SF`}
        />
      </div>
    </Card>
  )
}
