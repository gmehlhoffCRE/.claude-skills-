import { C, PROPERTY_TYPE_COLORS, REGION_COLORS, REGION_ORDER, SEGMENT_COLORS, colorFor } from '../tokens'
import type { Lease } from '../types'

/** Every number on screen is derived here from the fetched rows — nothing is pre-aggregated. */

export interface MetricsOptions {
  /** "Today" for the whole dashboard. Always UTC midnight so buckets don't shift by timezone. */
  asOf: Date
  expiringMonths: number
  runwayMonths: number
}

export const utcToday = (): Date => {
  const now = new Date()
  return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()))
}

export const addMonths = (d: Date, months: number): Date =>
  new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + months, d.getUTCDate()))

const sum = <T,>(xs: T[], f: (x: T) => number): number => xs.reduce((a, x) => a + f(x), 0)

export interface Slice {
  name: string
  value: number
  color: string
  share: number
}

export interface RegionAggregate {
  name: string
  count: number
  sf: number
  agr: number
  psf: number
  color: string
  /** Width of the bar relative to the largest region by AGR. */
  barPct: number
}

export interface YearBucket {
  /** "2027" or "2032+" */
  key: string
  label: string
  leases: Lease[]
  sf: number
  agr: number
  isOverflow: boolean
}

export interface RunwayRow {
  lease: Lease
  /** Bar width as a percentage of the runway window. */
  widthPct: number
  /** Set when the lease expires past the window; rendered as a "→ Mar '38" tail. */
  tail: string
  color: string
  expiringSoon: boolean
}

export interface AttentionRow {
  lease: Lease
  flag: 'CLOSING' | 'SUBLEASE'
}

export interface Metrics {
  asOf: Date
  horizon: Date
  expiringMonths: number
  runwayMonths: number
  leases: Lease[]
  totalSf: number
  totalAgr: number
  blendedPsf: number
  expiringSoon: Lease[]
  active: Lease[]
  regionCount: number
  marketCount: number
  segments: Slice[]
  propertyTypes: Slice[]
  regions: RegionAggregate[]
  yearBuckets: YearBucket[]
  maxYearSf: number
  top5: Lease[]
  attention: AttentionRow[]
  pipeline: Lease[]
  runwayRows: RunwayRow[]
  runwayTicks: { label: string; leftPct: number }[]
  mtmCount: number
}

const CLOSING_RE = /clos/i
const SUBLEASE_RE = /subleas/i

/** A note mentioning closing (and not a sublease) marks the lease as closing at expiration. */
export const isClosing = (lease: Lease): boolean =>
  CLOSING_RE.test(lease.note) && !SUBLEASE_RE.test(lease.note)

export const needsAttention = (lease: Lease): boolean =>
  CLOSING_RE.test(lease.note) || SUBLEASE_RE.test(lease.note)

export const isExpiringSoon = (lease: Lease, horizon: Date): boolean =>
  lease.expDate !== null && lease.expDate < horizon

/** CSS conic-gradient string for a donut, in slice order. */
export const conicGradient = (slices: Slice[]): string => {
  if (!slices.length) return C.hairline
  let acc = 0
  const stops = slices.map((s) => {
    const from = acc
    acc += s.share * 360
    return `${s.color} ${from.toFixed(2)}deg ${acc.toFixed(2)}deg`
  })
  return `conic-gradient(${stops.join(',')})`
}

const toSlices = (
  totals: Map<string, number>,
  colors: Record<string, string>,
  total: number,
): Slice[] =>
  [...totals.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([name, value]) => ({
      name: name || '—',
      value,
      color: colorFor(colors, name),
      share: total > 0 ? value / total : 0,
    }))

const tally = (leases: Lease[], key: (l: Lease) => string, val: (l: Lease) => number) => {
  const m = new Map<string, number>()
  for (const l of leases) m.set(key(l), (m.get(key(l)) ?? 0) + val(l))
  return m
}

export function buildMetrics(leases: Lease[], opts: MetricsOptions): Metrics {
  const { asOf, expiringMonths, runwayMonths } = opts
  const horizon = addMonths(asOf, expiringMonths)

  const totalSf = sum(leases, (l) => l.sf)
  const totalAgr = sum(leases, (l) => l.agr)
  const expiringSoon = leases.filter((l) => isExpiringSoon(l, horizon))
  const active = leases.filter((l) => l.status === 'Active')

  const segments = toSlices(
    tally(leases, (l) => l.seg, (l) => l.agr),
    SEGMENT_COLORS,
    totalAgr,
  )
  const propertyTypes = toSlices(
    tally(leases, (l) => l.type, (l) => l.sf),
    PROPERTY_TYPE_COLORS,
    totalSf,
  )

  // Regions: the six canonical ones in spec order, then any extra value the sheet contains.
  const presentRegions = [...new Set(leases.map((l) => l.region).filter(Boolean))]
  const orderedRegionNames = [
    ...REGION_ORDER.filter((r) => presentRegions.includes(r)),
    ...presentRegions.filter((r) => !(REGION_ORDER as readonly string[]).includes(r)),
  ]
  const regionRaw = orderedRegionNames.map((name) => {
    const rs = leases.filter((l) => l.region === name)
    const sf = sum(rs, (l) => l.sf)
    const agr = sum(rs, (l) => l.agr)
    return { name, count: rs.length, sf, agr, psf: sf > 0 ? agr / sf : 0 }
  })
  const maxRegionAgr = Math.max(1, ...regionRaw.map((r) => r.agr))
  const regions: RegionAggregate[] = regionRaw.map((r) => ({
    ...r,
    color: colorFor(REGION_COLORS, r.name),
    barPct: (r.agr / maxRegionAgr) * 100,
  }))

  // Expiration years: six calendar years from the current one, then an overflow bucket.
  const baseYear = asOf.getUTCFullYear()
  const years = Array.from({ length: 6 }, (_, i) => baseYear + i)
  const overflowYear = baseYear + 6
  const yearBuckets: YearBucket[] = [
    ...years.map((y) => {
      const ls = leases.filter((l) => l.expDate?.getUTCFullYear() === y)
      return {
        key: String(y),
        label: `'${String(y).slice(2)}`,
        leases: ls,
        sf: sum(ls, (l) => l.sf),
        agr: sum(ls, (l) => l.agr),
        isOverflow: false,
      }
    }),
    (() => {
      const ls = leases.filter(
        (l) => l.expDate !== null && l.expDate.getUTCFullYear() >= overflowYear,
      )
      return {
        key: `${overflowYear}+`,
        label: `'${String(overflowYear).slice(2)}+`,
        leases: ls,
        sf: sum(ls, (l) => l.sf),
        agr: sum(ls, (l) => l.agr),
        isOverflow: true,
      }
    })(),
  ]
  const maxYearSf = Math.max(1, ...yearBuckets.map((b) => b.sf))

  const top5 = [...leases].sort((a, b) => b.agr - a.agr).slice(0, 5)

  const byExpiration = (a: Lease, b: Lease): number =>
    (a.expDate?.getTime() ?? Number.MAX_SAFE_INTEGER) -
    (b.expDate?.getTime() ?? Number.MAX_SAFE_INTEGER)

  const attention: AttentionRow[] = leases
    .filter(needsAttention)
    .sort(byExpiration)
    .map((lease) => ({ lease, flag: isClosing(lease) ? 'CLOSING' : 'SUBLEASE' }))

  const pipeline = [...active].sort(byExpiration)

  // Runway: bar width is months-to-expiration as a share of the window.
  const AVG_MONTH_MS = 30.44 * 864e5
  const monthsOut = (d: Date): number => (d.getTime() - asOf.getTime()) / AVG_MONTH_MS
  const runwayRows: RunwayRow[] = [...leases].sort(byExpiration).map((lease) => {
    const m = lease.expDate ? monthsOut(lease.expDate) : 0
    const beyond = lease.expDate !== null && m > runwayMonths
    return {
      lease,
      widthPct: lease.expDate ? Math.min(100, Math.max(1.5, (m / runwayMonths) * 100)) : 1.5,
      tail: beyond ? `→ ${lease.expDate ? formatTail(lease.expDate) : ''}` : lease.expDate ? '' : 'MTM',
      color: isClosing(lease)
        ? C.danger
        : lease.status === 'Active'
          ? C.goldenrod
          : C.midnight,
      expiringSoon: isExpiringSoon(lease, horizon),
    }
  })

  // One tick per January inside the window.
  const runwayTicks: { label: string; leftPct: number }[] = []
  for (let y = baseYear + 1; ; y++) {
    const jan = new Date(Date.UTC(y, 0, 1))
    const leftPct = (monthsOut(jan) / runwayMonths) * 100
    if (leftPct > 100) break
    runwayTicks.push({ label: `'${String(y).slice(2)}`, leftPct })
  }

  return {
    asOf,
    horizon,
    expiringMonths,
    runwayMonths,
    leases,
    totalSf,
    totalAgr,
    blendedPsf: totalSf > 0 ? totalAgr / totalSf : 0,
    expiringSoon,
    active,
    regionCount: presentRegions.length,
    marketCount: new Set(leases.map((l) => `${l.city}|${l.st}`)).size,
    segments,
    propertyTypes,
    regions,
    yearBuckets,
    maxYearSf,
    top5,
    attention,
    pipeline,
    runwayRows,
    runwayTicks,
    mtmCount: leases.filter((l) => l.isMtm).length,
  }
}

const formatTail = (d: Date): string =>
  d
    .toLocaleDateString('en-US', { month: 'short', year: '2-digit', timeZone: 'UTC' })
    .replace(' ', " '")
