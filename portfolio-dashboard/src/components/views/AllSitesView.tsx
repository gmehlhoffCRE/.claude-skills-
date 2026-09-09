import { useMemo, useState } from 'react'
import { C, REGION_ORDER } from '../../tokens'
import { fmtDate, fmtInt, fmtMoney, fmtMoneyExact, fmtPsf, fmtSf } from '../../lib/format'
import { isExpiringSoon, type Metrics } from '../../lib/metrics'
import type { Lease } from '../../types'
import { Card } from '../Card'

type SortKey =
  | 'city'
  | 'region'
  | 'seg'
  | 'type'
  | 'leaseType'
  | 'addr'
  | 'sf'
  | 'exp'
  | 'agr'
  | 'psf'
  | 'status'
  | 'note'

interface ColumnDef {
  key: SortKey
  label: string
  numeric?: boolean
}

const COLUMNS: ColumnDef[] = [
  { key: 'city', label: 'City / Market' },
  { key: 'region', label: 'Region' },
  { key: 'seg', label: 'Segment' },
  { key: 'type', label: 'Prop Type' },
  { key: 'leaseType', label: 'Lease Type' },
  { key: 'addr', label: 'Street Address' },
  { key: 'sf', label: 'SF', numeric: true },
  { key: 'exp', label: 'Expires' },
  { key: 'agr', label: 'Annual Rent', numeric: true },
  { key: 'psf', label: '$/SF', numeric: true },
  { key: 'status', label: 'Status' },
  { key: 'note', label: 'Cresa Notes' },
]

const sortValue = (l: Lease, key: SortKey): string | number => {
  switch (key) {
    case 'exp':
      // MTM / unknown sorts last in ascending order.
      return l.expDate ? l.expDate.getTime() : Number.MAX_SAFE_INTEGER
    case 'sf':
      return l.sf
    case 'agr':
      return l.agr
    case 'psf':
      return l.psf ?? 0
    case 'city':
      return `${l.city} ${l.st}`
    default:
      return l[key] ?? ''
  }
}

/** Full data table: search + region filter + sortable headers, all combining. */
export function AllSitesView({ m }: { m: Metrics }) {
  const [search, setSearch] = useState('')
  const [region, setRegion] = useState<string | null>(null)
  const [sortKey, setSortKey] = useState<SortKey>('agr')
  const [sortDir, setSortDir] = useState<-1 | 1>(-1)

  const regionsPresent = useMemo(() => {
    const present = new Set(m.leases.map((l) => l.region).filter(Boolean))
    const ordered = REGION_ORDER.filter((r) => present.has(r)) as string[]
    return [...ordered, ...[...present].filter((r) => !ordered.includes(r))]
  }, [m.leases])

  const rows = useMemo(() => {
    const q = search.trim().toLowerCase()
    const filtered = m.leases.filter((l) => {
      if (region && l.region !== region) return false
      if (!q) return true
      return [l.city, l.st, l.addr, l.seg, l.region, l.type, l.leaseType, l.note]
        .join(' ')
        .toLowerCase()
        .includes(q)
    })
    return filtered.sort((a, b) => {
      const x = sortValue(a, sortKey)
      const y = sortValue(b, sortKey)
      if (typeof x === 'string' && typeof y === 'string') return sortDir * x.localeCompare(y)
      return sortDir * ((x as number) - (y as number))
    })
  }, [m.leases, search, region, sortKey, sortDir])

  const shownSf = rows.reduce((a, l) => a + l.sf, 0)
  const shownAgr = rows.reduce((a, l) => a + l.agr, 0)

  const onSort = (col: ColumnDef) => {
    if (col.key === sortKey) setSortDir((d) => (d === 1 ? -1 : 1))
    else {
      setSortKey(col.key)
      setSortDir(col.numeric ? -1 : 1)
    }
  }

  return (
    <div className="view" style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
      <Card style={{ flex: 1 }}>
        <div className="tbl-toolbar">
          <h2 className="card-title" style={{ marginRight: 6 }}>
            All Sites · {rows.length} of {m.leases.length}
          </h2>
          <input
            className="tbl-search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search city, address, segment…"
            aria-label="Search sites"
          />
          <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
            <button
              className="pill"
              aria-pressed={region === null}
              onClick={() => setRegion(null)}
            >
              All
            </button>
            {regionsPresent.map((r) => (
              <button
                key={r}
                className="pill"
                aria-pressed={region === r}
                onClick={() => setRegion(region === r ? null : r)}
              >
                {r}
              </button>
            ))}
          </div>
          <div className="spacer" />
          <div className="tbl-totals">
            Filtered: <b>{fmtSf(shownSf)} SF</b> · <b>{fmtMoney(shownAgr)}</b> AGR · click headers to
            sort
          </div>
        </div>

        <div className="tbl-scroll">
          <div style={{ minWidth: 1280 }}>
            <div className="tbl-grid tbl-head">
              {COLUMNS.map((col) => {
                const active = sortKey === col.key
                return (
                  <button
                    key={col.key}
                    className={`tbl-th${col.numeric ? ' r' : ''}`}
                    aria-sort={active ? (sortDir > 0 ? 'ascending' : 'descending') : 'none'}
                    onClick={() => onSort(col)}
                  >
                    {col.label}
                    {active ? (sortDir > 0 ? ' ▴' : ' ▾') : ''}
                  </button>
                )
              })}
            </div>
            {rows.map((l, i) => {
              const soon = isExpiringSoon(l, m.horizon)
              return (
                <div
                  className="tbl-grid tbl-row"
                  key={l.id}
                  style={{ background: i % 2 ? C.zebra : '#fff' }}
                >
                  <div className="tbl-td city">
                    {l.city}
                    {l.st ? `, ${l.st}` : ''}
                  </div>
                  <div className="tbl-td">{l.region}</div>
                  <div className="tbl-td">{l.seg}</div>
                  <div className="tbl-td">{l.type}</div>
                  <div className="tbl-td muted">{l.leaseType}</div>
                  <div className="tbl-td muted">{l.addr}</div>
                  <div className="tbl-td num mono-num">{fmtInt(l.sf)}</div>
                  <div
                    className="tbl-td"
                    style={{ fontSize: 12, fontWeight: 700, color: soon ? C.warn : C.bodySoft }}
                  >
                    {fmtDate(l.expDate)}
                  </div>
                  <div className="tbl-td num mono-num" style={{ fontWeight: 700 }}>
                    {fmtMoneyExact(l.agr)}
                  </div>
                  <div className="tbl-td num mono-num muted">{fmtPsf(l.psf)}</div>
                  <div className="tbl-td chip-cell">
                    <span className={`chip ${l.status === 'Active' ? 'chip-active' : 'chip-none'}`}>
                      {l.status === 'Active' ? 'Active' : '—'}
                    </span>
                  </div>
                  <div className="tbl-td note">{l.note}</div>
                </div>
              )
            })}
            {rows.length === 0 && (
              <div style={{ padding: '18px 12px', fontSize: 12, color: C.muted }}>
                No sites match this search and filter.
              </div>
            )}
          </div>
        </div>
      </Card>
    </div>
  )
}
