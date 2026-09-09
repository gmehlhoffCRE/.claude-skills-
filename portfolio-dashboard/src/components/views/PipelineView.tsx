import { C } from '../../tokens'
import { fmtDate, fmtInt, fmtMoney } from '../../lib/format'
import { isExpiringSoon, type Metrics } from '../../lib/metrics'
import { Card } from '../Card'

/** Open transactions only (TRANSACTION STATUS = Active), sorted by expiration. */
export function PipelineView({ m }: { m: Metrics }) {
  return (
    <div className="view">
      <Card
        title="Active Transaction Pipeline"
        hint={`${m.pipeline.length} open transaction${
          m.pipeline.length === 1 ? '' : 's'
        } · sorted by expiration`}
      >
        <div style={{ overflowX: 'auto' }}>
          <div style={{ minWidth: 760 }}>
            <div className="pl-grid pl-head">
              <div style={{ paddingLeft: 0 }}>Location</div>
              <div>Expires</div>
              <div style={{ textAlign: 'right' }}>SF</div>
              <div style={{ textAlign: 'right' }}>AGR</div>
              <div style={{ padding: '9px 0 9px 16px' }}>Status / Next Step</div>
            </div>
            {m.pipeline.length === 0 && (
              <div style={{ padding: '18px 16px', fontSize: 12, color: C.muted }}>
                No leases are marked Active in the sheet.
              </div>
            )}
            {m.pipeline.map((l, i) => (
              <div
                className="pl-grid pl-row"
                key={l.id}
                style={{ background: i % 2 ? C.zebra : '#fff' }}
              >
                <div style={{ padding: '9px 8px 9px 0', minWidth: 0 }}>
                  <div className="pl-city">
                    {l.city}
                    {l.st ? `, ${l.st}` : ''}
                  </div>
                  <div className="pl-addr">{l.addr}</div>
                </div>
                <div
                  style={{
                    padding: '9px 8px',
                    fontSize: 12,
                    fontWeight: 700,
                    whiteSpace: 'nowrap',
                    color: isExpiringSoon(l, m.horizon) ? C.warn : C.bodySoft,
                  }}
                >
                  {fmtDate(l.expDate)}
                </div>
                <div className="mono-num" style={{ padding: '9px 8px', fontSize: 12, textAlign: 'right', color: C.bodySoft }}>
                  {fmtInt(l.sf)}
                </div>
                <div
                  className="mono-num"
                  style={{ padding: '9px 8px', fontSize: 12, fontWeight: 700, textAlign: 'right', color: C.bodySoft }}
                >
                  {fmtMoney(l.agr)}
                </div>
                <div className="pl-note">{l.note || '—'}</div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  )
}
