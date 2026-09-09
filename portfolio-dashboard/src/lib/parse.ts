import type { Lease, TransactionStatus } from '../types'

/** Header matching is forgiving: case, spacing, and punctuation in the sheet may drift. */
const normalizeHeader = (h: string): string =>
  h
    .toLowerCase()
    .replace(/\(.*?\)/g, ' ')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()

/** Canonical field -> accepted header spellings (already normalized). */
const HEADER_ALIASES: Record<keyof FieldMap, string[]> = {
  leaseType: ['lease type'],
  region: ['region'],
  status: ['transaction status', 'status'],
  seg: ['operating segment', 'segment'],
  city: ['lease city', 'city', 'city market'],
  st: ['st', 'state', 'state province', 'country'],
  addr: ['street address', 'address'],
  type: ['property type', 'prop type'],
  sf: ['sf', 'rentable sf', 'square feet'],
  exp: ['lease exp', 'lease expiration', 'expiration', 'expires'],
  agr: ['annual gross rent', 'annual gross rent us', 'annual rent', 'agr'],
  note: ['cresa notes', 'notes', 'note'],
  lat: ['lat', 'latitude'],
  lng: ['lng', 'lon', 'long', 'longitude'],
}

interface FieldMap {
  leaseType: number
  region: number
  status: number
  seg: number
  city: number
  st: number
  addr: number
  type: number
  sf: number
  exp: number
  agr: number
  note: number
  lat: number
  lng: number
}

export interface ParseResult {
  leases: Lease[]
  warnings: string[]
}

/** Resolves each canonical field to a column index, or -1 when the sheet lacks it. */
export function mapHeaders(header: string[]): { map: FieldMap; unknown: number[] } {
  const normalized = header.map(normalizeHeader)
  const map = {} as FieldMap
  const claimed = new Set<number>()
  for (const [field, aliases] of Object.entries(HEADER_ALIASES) as [
    keyof FieldMap,
    string[],
  ][]) {
    const idx = normalized.findIndex((h, i) => !claimed.has(i) && aliases.includes(h))
    map[field] = idx
    if (idx >= 0) claimed.add(idx)
  }
  const unknown = header.map((_, i) => i).filter((i) => !claimed.has(i) && header[i]?.trim())
  return { map, unknown }
}

/** Strips $ , % and whitespace; returns null for blanks and non-numbers. */
export function toNumber(raw: unknown): number | null {
  if (raw === null || raw === undefined) return null
  if (typeof raw === 'number') return Number.isFinite(raw) ? raw : null
  const cleaned = String(raw).replace(/[$,\s]/g, '').replace(/^\((.*)\)$/, '-$1')
  if (cleaned === '' || cleaned === '—' || cleaned === '-') return null
  const n = Number(cleaned)
  return Number.isFinite(n) ? n : null
}

const EXCEL_EPOCH_MS = Date.UTC(1899, 11, 30)
/** Serials below this are almost certainly a typo, not a 1900s date we'd ever see in a lease. */
const MIN_PLAUSIBLE_SERIAL = 20000 // ~1954
const MAX_PLAUSIBLE_SERIAL = 80000 // ~2119

export interface ParsedExpiration {
  date: Date | null
  isMtm: boolean
  ok: boolean
}

/**
 * LEASE EXP arrives as an Excel serial, an ISO date, a locale-formatted date, or "MTM".
 * Anything unrecognized is treated as unknown (renders as MTM) and reported as a warning.
 */
export function parseExpiration(raw: unknown): ParsedExpiration {
  if (raw === null || raw === undefined) return { date: null, isMtm: false, ok: false }
  const s = String(raw).trim()
  if (s === '') return { date: null, isMtm: false, ok: false }
  if (/^m[\s-]?t[\s-]?m$/i.test(s) || /month.to.month/i.test(s))
    return { date: null, isMtm: true, ok: true }

  const serial = Number(s.replace(/,/g, ''))
  if (Number.isFinite(serial) && /^[\d.,]+$/.test(s)) {
    if (serial >= MIN_PLAUSIBLE_SERIAL && serial <= MAX_PLAUSIBLE_SERIAL) {
      return { date: new Date(EXCEL_EPOCH_MS + serial * 864e5), isMtm: false, ok: true }
    }
    return { date: null, isMtm: false, ok: false }
  }

  // ISO (yyyy-mm-dd) — parse as UTC so a negative local offset can't shift the month.
  const iso = /^(\d{4})-(\d{2})-(\d{2})/.exec(s)
  if (iso) {
    return {
      date: new Date(Date.UTC(+iso[1], +iso[2] - 1, +iso[3])),
      isMtm: false,
      ok: true,
    }
  }

  // US formatted (m/d/yyyy or m-d-yy).
  const us = /^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$/.exec(s)
  if (us) {
    const year = +us[3] < 100 ? 2000 + +us[3] : +us[3]
    return { date: new Date(Date.UTC(year, +us[1] - 1, +us[2])), isMtm: false, ok: true }
  }

  // Anything else Date can read ("Sep 1, 2026", "1 Sep 2026") — normalize to UTC midnight.
  const loose = new Date(s)
  if (!Number.isNaN(loose.getTime())) {
    return {
      date: new Date(
        Date.UTC(loose.getFullYear(), loose.getMonth(), loose.getDate()),
      ),
      isMtm: false,
      ok: true,
    }
  }
  return { date: null, isMtm: false, ok: false }
}

const cell = (row: unknown[], idx: number): string =>
  idx >= 0 && row[idx] !== undefined && row[idx] !== null ? String(row[idx]).trim() : ''

const isActive = (raw: string): TransactionStatus =>
  /^active$/i.test(raw.trim()) ? 'Active' : 'Inactive'

/**
 * Turns a header row + data rows into Lease records.
 * A row is skipped (with a warning) only when it has no city AND no address — otherwise
 * we render what we have, because a partly-filled row still belongs in the portfolio.
 */
export function parseRows(header: string[], rows: unknown[][]): ParseResult {
  const { map, unknown } = mapHeaders(header)
  const warnings: string[] = []

  const missing = (['city', 'sf', 'agr', 'exp'] as (keyof FieldMap)[]).filter(
    (f) => map[f] < 0,
  )
  if (missing.length) {
    warnings.push(
      `Sheet is missing expected column(s): ${missing.join(', ')}. Check the header row against SETUP.md.`,
    )
  }

  const leases: Lease[] = []
  rows.forEach((row, i) => {
    const rowNumber = i + 2 // 1-based, after the header row
    const city = cell(row, map.city)
    const addr = cell(row, map.addr)
    if (!city && !addr) return // blank spacer row — silently ignored

    const sf = toNumber(row[map.sf]) ?? 0
    const agr = toNumber(row[map.agr]) ?? 0
    const expRaw = cell(row, map.exp)
    const exp = parseExpiration(expRaw)
    if (!exp.ok && expRaw)
      warnings.push(`Row ${rowNumber} (${city || addr}): unreadable LEASE EXP "${expRaw}".`)

    const lat = toNumber(row[map.lat])
    const lng = toNumber(row[map.lng])
    if (lat === null || lng === null)
      warnings.push(`Row ${rowNumber} (${city || addr}): missing LAT/LNG — omitted from map.`)

    const extra: Record<string, string> = {}
    for (const idx of unknown) {
      const v = cell(row, idx)
      if (v) extra[header[idx].trim()] = v
    }

    leases.push({
      id: `${rowNumber}-${city}-${addr}`.toLowerCase().replace(/\s+/g, '-'),
      leaseType: cell(row, map.leaseType),
      region: cell(row, map.region),
      status: isActive(cell(row, map.status)),
      seg: cell(row, map.seg),
      city,
      st: cell(row, map.st),
      addr,
      type: cell(row, map.type),
      sf,
      expRaw,
      expDate: exp.date,
      isMtm: exp.isMtm,
      agr,
      note: cell(row, map.note),
      lat,
      lng,
      psf: sf > 0 ? agr / sf : null,
      extra,
    })
  })

  return { leases, warnings }
}

/** RFC 4180 CSV parser — handles quoted fields, embedded commas, newlines, and "" escapes. */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = []
  let row: string[] = []
  let field = ''
  let inQuotes = false
  for (let i = 0; i < text.length; i++) {
    const ch = text[i]
    if (inQuotes) {
      if (ch === '"') {
        if (text[i + 1] === '"') {
          field += '"'
          i++
        } else inQuotes = false
      } else field += ch
      continue
    }
    if (ch === '"') inQuotes = true
    else if (ch === ',') {
      row.push(field)
      field = ''
    } else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++
      row.push(field)
      rows.push(row)
      row = []
      field = ''
    } else field += ch
  }
  if (field !== '' || row.length) {
    row.push(field)
    rows.push(row)
  }
  return rows.filter((r) => r.some((c) => c.trim() !== ''))
}
