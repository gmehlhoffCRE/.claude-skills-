import { Fragment } from 'react'
import { C } from '../../tokens'
import { fmtDate, fmtInt, fmtMoney, fmtSf } from '../../lib/format'
import type { Metrics } from '../../lib/metrics'
import { Card } from '../Card'

/** Runway (Gantt-style) plus a by-year rail. Bar length = time remaining on the lease. */
export function ExpirationsView({ m }: { m: Metrics }) {
  return (
    <div className="view exp-view">
      <Card
        title="Lease Expiration Runway"
        hint={
          <span className="exp-legend">
            <span>
              <i style={{ background: C.goldenrod }} />
              active transaction
            </span>
            <span>
              <i style={{ background: C.midnight }} />
              no action yet
            </span>
            <span>
              <i style={{ background: C.danger }} />
              closing at expiration
            </span>
          </span>
        }
      >
        <div style={{ overflowX: 'auto' }}>
          <div style={{ minWidth: 960, padding: '8px 16px 16px' }}>
            <div className="exp-grid">
              <div className="exp-h exp-h-loc">Location</div>
              <div className="exp-axis">
                {m.runwayTicks.map((t) => (
                  <div className="exp-tick" key={t.label} style={{ left: `${t.leftPct}%` }}>
                    {t.label}
                  </div>
                ))}
              </div>
              <div className="exp-h exp-h-r">Expires</div>
              <div className="exp-h exp-h-r">SF</div>
              <div className="exp-h exp-h-r">AGR</div>

              {m.runwayRows.map((row, i) => {
                const zebra = i % 2 ? C.zebra : '#fff'
                const { lease } = row
                return (
                  <Fragment key={lease.id}>
                    <div className="exp-cell exp-city" style={{ background: zebra }}>
                      <div>
                        {lease.city}
                        {lease.st ? `, ${lease.st}` : ''}
                      </div>
                    </div>
                    <div className="exp-cell exp-track" style={{ background: zebra }}>
                      <div
                        className="exp-bar"
                        style={{ width: `${row.widthPct}%`, background: row.color }}
                      />
                      {row.tail && lease.expDate && <span className="exp-tail">{row.tail}</span>}
                      {!lease.expDate && <span className="exp-stub">MTM</span>}
                    </div>
                    <div
                      className="exp-cell exp-date"
                      style={{ background: zebra, color: row.expiringSoon ? C.warn : C.bodySoft }}
                    >
                      {fmtDate(lease.expDate)}
                    </div>
                    <div className="exp-cell exp-num mono-num" style={{ background: zebra }}>
                      {fmtInt(lease.sf)}
                    </div>
                    <div className="exp-cell exp-num mono-num" style={{ background: zebra }}>
                      {fmtMoney(lease.agr)}
                    </div>
                  </Fragment>
                )
              })}
            </div>
          </div>
        </div>
      </Card>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <h2 className="card-title" style={{ padding: '2px 0' }}>
          By Expiration Year
        </h2>
        {m.yearBuckets.map((b, i) => (
          <div
            className="year-card"
            key={b.key}
            style={{ borderLeft: `3px solid ${i < 2 ? C.goldenrod : C.midnight}` }}
          >
            <div>
              <div className="year-label">{b.key}</div>
              <div className="year-n">
                {b.leases.length}{' '}
                <span className="year-unit">{b.leases.length === 1 ? 'lease' : 'leases'}</span>
              </div>
            </div>
            <div className="year-side">
              {fmtSf(b.sf)} SF
              <br />
              {fmtMoney(b.agr)}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
