import { fmtDate, fmtInt, fmtMoneyExact, fmtPsf } from '../../lib/format'
import type { Lease } from '../../types'

/** Click-a-dot detail panel, pinned top-right inside the map card. */
export function PropertyDetail({ lease, onClose }: { lease: Lease; onClose: () => void }) {
  const fields: [string, string][] = [
    ['Operating Segment', lease.seg || '—'],
    ['Region', lease.region || '—'],
    ['Property Type', lease.type || '—'],
    ['Lease Type', lease.leaseType || '—'],
    ['Rentable SF', fmtInt(lease.sf)],
    ['Expires', fmtDate(lease.expDate)],
    ['Annual Gross Rent', fmtMoneyExact(lease.agr)],
    ['Rent / SF', fmtPsf(lease.psf)],
    ['Transaction', lease.status === 'Active' ? 'Active' : 'None'],
  ]

  return (
    <div className="detail" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Property detail">
      <button className="d-close" onClick={onClose} aria-label="Close detail">
        ×
      </button>
      <div className="d-name">
        {lease.city}
        {lease.st ? `, ${lease.st}` : ''}
      </div>
      <div className="d-addr">{lease.addr}</div>
      <div className="d-grid">
        {fields.map(([label, value]) => (
          <div className="d-field" key={label}>
            <div className="d-label">{label}</div>
            <div className="d-val">{value}</div>
          </div>
        ))}
      </div>
      {lease.note && (
        <div className="d-note">
          <b>Cresa Note</b>
          {lease.note}
        </div>
      )}
    </div>
  )
}
