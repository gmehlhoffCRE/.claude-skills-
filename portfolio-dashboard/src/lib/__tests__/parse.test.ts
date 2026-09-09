import { describe, expect, it } from 'vitest'
import { mapHeaders, parseCsv, parseExpiration, parseRows, toNumber } from '../parse'
import { FIXTURE_HEADER, FIXTURE_ROWS } from '../../dev/fixture'

describe('parseExpiration', () => {
  it('converts Excel serials using the 1899-12-30 epoch', () => {
    const { date } = parseExpiration(46965)
    expect(date?.toISOString().slice(0, 10)).toBe('2028-07-31')
  })

  it('recognizes month-to-month in several spellings', () => {
    for (const raw of ['MTM', 'mtm', 'M-T-M', 'month-to-month']) {
      expect(parseExpiration(raw)).toMatchObject({ isMtm: true, date: null, ok: true })
    }
  })

  it('parses ISO dates in UTC regardless of local timezone', () => {
    expect(parseExpiration('2027-01-31').date?.toISOString().slice(0, 10)).toBe('2027-01-31')
  })

  it('parses US-formatted dates, including 2-digit years', () => {
    expect(parseExpiration('9/30/2029').date?.toISOString().slice(0, 10)).toBe('2029-09-30')
    expect(parseExpiration('9/30/29').date?.toISOString().slice(0, 10)).toBe('2029-09-30')
  })

  it('parses long-form dates', () => {
    expect(parseExpiration('Sep 30, 2029').date?.toISOString().slice(0, 10)).toBe('2029-09-30')
  })

  it('reports blanks and junk as unreadable rather than guessing', () => {
    expect(parseExpiration('').ok).toBe(false)
    expect(parseExpiration('tbd').ok).toBe(false)
    expect(parseExpiration(12).ok).toBe(false) // implausible serial
  })
})

describe('toNumber', () => {
  it('strips currency formatting', () => {
    expect(toNumber('$1,150,175')).toBe(1150175)
    expect(toNumber(' 8,746 ')).toBe(8746)
    expect(toNumber('(500)')).toBe(-500)
  })

  it('returns null for blanks and dashes', () => {
    expect(toNumber('')).toBeNull()
    expect(toNumber('—')).toBeNull()
    expect(toNumber(undefined)).toBeNull()
  })
})

describe('mapHeaders', () => {
  it('matches the canonical schema regardless of case and punctuation', () => {
    const { map } = mapHeaders([
      'Lease Type',
      'region',
      'TRANSACTION STATUS',
      'Operating Segment',
      'Lease City',
      'ST',
      'Street Address',
      'Property Type',
      'SF',
      'Lease Exp',
      'Annual Gross Rent ($US)',
      'Cresa Notes',
      'Lat',
      'Lng',
    ])
    expect(map.leaseType).toBe(0)
    expect(map.agr).toBe(10)
    expect(map.lng).toBe(13)
  })

  it('reports columns outside the schema so they can be preserved', () => {
    const { unknown } = mapHeaders([...FIXTURE_HEADER, 'HEADCOUNT'])
    expect(unknown).toEqual([FIXTURE_HEADER.length])
  })
})

describe('parseRows', () => {
  it('normalizes the sample sheet into 60 leases with derived psf', () => {
    const { leases, warnings } = parseRows(FIXTURE_HEADER, FIXTURE_ROWS)
    expect(leases).toHaveLength(60)
    expect(warnings).toHaveLength(0)
    const houston = leases.find((l) => l.city === 'Houston HQ')!
    expect(houston.sf).toBe(50380)
    expect(houston.psf).toBeCloseTo(1150175 / 50380, 6)
    expect(houston.expDate?.getUTCFullYear()).toBe(2036)
  })

  it('flags month-to-month leases without dropping them', () => {
    const { leases } = parseRows(FIXTURE_HEADER, FIXTURE_ROWS)
    const mtm = leases.filter((l) => l.isMtm)
    expect(mtm).toHaveLength(1)
    expect(mtm[0].city).toBe('Chorley')
    expect(mtm[0].expDate).toBeNull()
  })

  it('keeps partial rows, warns about missing coordinates, and skips blank ones', () => {
    const { leases, warnings } = parseRows(FIXTURE_HEADER, [
      ['Direct Lease', 'West', 'Active', 'Forensics', 'Boise', 'ID', '', 'Office', '1,000', '', '$50,000', '', '', ''],
      ['', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    ])
    expect(leases).toHaveLength(1)
    expect(leases[0].lat).toBeNull()
    expect(warnings.some((w) => w.includes('missing LAT/LNG'))).toBe(true)
  })

  it('warns when a required column is absent', () => {
    const { warnings } = parseRows(['LEASE CITY', 'SF'], [['Boise', '100']])
    expect(warnings[0]).toContain('missing expected column')
  })

  it('preserves unmapped columns for future schema growth', () => {
    const { leases } = parseRows(
      [...FIXTURE_HEADER, 'HEADCOUNT'],
      [[...FIXTURE_ROWS[0], '42']],
    )
    expect(leases[0].extra.HEADCOUNT).toBe('42')
  })
})

describe('parseCsv', () => {
  it('handles quoted fields with commas, newlines, and escaped quotes', () => {
    const rows = parseCsv('a,b\n"x, y","he said ""hi""\nnext"\n')
    expect(rows).toEqual([
      ['a', 'b'],
      ['x, y', 'he said "hi"\nnext'],
    ])
  })
})
