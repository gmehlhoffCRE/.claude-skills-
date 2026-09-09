import { describe, expect, it } from 'vitest'
import { FIXTURE_HEADER, FIXTURE_ROWS } from '../../dev/fixture'
import { parseRows } from '../parse'
import { addMonths, buildMetrics, conicGradient, isClosing } from '../metrics'
import type { Lease } from '../../types'

const leases = parseRows(FIXTURE_HEADER, FIXTURE_ROWS).leases
const asOf = new Date(Date.UTC(2026, 8, 1))
const m = buildMetrics(leases, { asOf, expiringMonths: 12, runwayMonths: 66 })

describe('buildMetrics totals', () => {
  it('sums footprint and rent from the rows', () => {
    expect(m.totalSf).toBe(leases.reduce((a, l) => a + l.sf, 0))
    expect(m.totalAgr).toBe(leases.reduce((a, l) => a + l.agr, 0))
    expect(m.blendedPsf).toBeCloseTo(m.totalAgr / m.totalSf, 9)
  })

  it('counts active transactions from TRANSACTION STATUS', () => {
    expect(m.active).toHaveLength(leases.filter((l) => l.status === 'Active').length)
    expect(m.pipeline).toHaveLength(m.active.length)
  })

  it('uses the configured window for expiring-soon', () => {
    const horizon = addMonths(asOf, 12)
    expect(m.horizon.getTime()).toBe(horizon.getTime())
    expect(m.expiringSoon.every((l) => l.expDate! < horizon)).toBe(true)
    const wider = buildMetrics(leases, { asOf, expiringMonths: 24, runwayMonths: 66 })
    expect(wider.expiringSoon.length).toBeGreaterThan(m.expiringSoon.length)
  })
})

describe('year buckets', () => {
  it('covers six calendar years plus an overflow bucket', () => {
    expect(m.yearBuckets.map((b) => b.key)).toEqual([
      '2026',
      '2027',
      '2028',
      '2029',
      '2030',
      '2031',
      '2032+',
    ])
  })

  it('puts every dated lease in exactly one bucket', () => {
    const dated = leases.filter((l) => l.expDate !== null).length
    expect(m.yearBuckets.reduce((a, b) => a + b.leases.length, 0)).toBe(dated)
  })

  it('routes the 2036 Houston HQ lease into the overflow bucket', () => {
    const overflow = m.yearBuckets.at(-1)!
    expect(overflow.leases.some((l) => l.city === 'Houston HQ')).toBe(true)
  })
})

describe('slices', () => {
  it('produces shares that sum to 1', () => {
    const sumShare = (xs: { share: number }[]) => xs.reduce((a, s) => a + s.share, 0)
    expect(sumShare(m.segments)).toBeCloseTo(1, 9)
    expect(sumShare(m.propertyTypes)).toBeCloseTo(1, 9)
  })

  it('sorts slices largest first and renders a full-circle gradient', () => {
    expect(m.segments[0].value).toBeGreaterThanOrEqual(m.segments[1].value)
    expect(conicGradient(m.segments)).toContain('360.00deg')
  })
})

describe('regions', () => {
  it('keeps the six canonical regions in spec order', () => {
    expect(m.regions.map((r) => r.name)).toEqual([
      'West',
      'Southeast',
      'South Central',
      'Northeast',
      'Canada',
      'International',
    ])
  })

  it('scales bars against the largest region by AGR', () => {
    expect(Math.max(...m.regions.map((r) => r.barPct))).toBe(100)
  })
})

describe('attention and runway', () => {
  it('flags closings and subleases from Cresa notes', () => {
    const flags = new Map(m.attention.map((a) => [a.lease.city, a.flag]))
    expect(flags.get('Melbourne')).toBe('CLOSING')
    expect(flags.get('Houston HQ')).toBe('SUBLEASE')
    expect(flags.get('Auckland')).toBe('SUBLEASE')
  })

  it('treats a note mentioning both closing and sublease as a sublease', () => {
    const lease = { note: 'Marketing for sublease before the office closes' } as Lease
    expect(isClosing(lease)).toBe(false)
  })

  it('clamps leases beyond the runway window and tags them with a tail label', () => {
    const houston = m.runwayRows.find((r) => r.lease.city === 'Houston HQ')!
    expect(houston.widthPct).toBe(100)
    expect(houston.tail).toMatch(/^→ /)
  })

  it('gives month-to-month leases a stub bar', () => {
    const chorley = m.runwayRows.find((r) => r.lease.city === 'Chorley')!
    expect(chorley.widthPct).toBe(1.5)
    expect(chorley.tail).toBe('MTM')
  })

  it('places one tick per January inside the window', () => {
    expect(m.runwayTicks.map((t) => t.label)).toEqual(["'27", "'28", "'29", "'30", "'31", "'32"])
    expect(m.runwayTicks.every((t) => t.leftPct > 0 && t.leftPct <= 100)).toBe(true)
  })
})

describe('empty portfolio', () => {
  it('renders zeros instead of dividing by zero', () => {
    const empty = buildMetrics([], { asOf, expiringMonths: 12, runwayMonths: 66 })
    expect(empty.blendedPsf).toBe(0)
    expect(empty.regions).toEqual([])
    expect(empty.maxYearSf).toBe(1)
    expect(conicGradient([])).toBe('#EEF0F4')
  })
})
