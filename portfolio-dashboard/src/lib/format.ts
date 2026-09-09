/** Number/date formatting shared by every view. Matches the design spec exactly. */

/** $8.04M / $130K / $940 */
export const fmtMoney = (n: number): string => {
  if (!Number.isFinite(n)) return '—'
  if (Math.abs(n) >= 1e6) return `$${(n / 1e6).toFixed(2)}M`
  if (Math.abs(n) >= 1e3) return `$${Math.round(n / 1e3)}K`
  return `$${Math.round(n)}`
}

/** 324K / 8.7K / 600 */
export const fmtSf = (n: number): string => {
  if (!Number.isFinite(n)) return '—'
  if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(Math.abs(n) >= 10e3 ? 0 : 1)}K`
  return `${Math.round(n)}`
}

/** Sep '26 — MTM/unknown expirations render as "MTM". */
export const fmtDate = (d: Date | null): string =>
  d
    ? d
        .toLocaleDateString('en-US', { month: 'short', year: '2-digit', timeZone: 'UTC' })
        .replace(' ', " '")
    : 'MTM'

/** September 9, 2026 — used in the header "as of" line. */
export const fmtLongDate = (d: Date): string =>
  d.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  })

export const fmtInt = (n: number): string =>
  Number.isFinite(n) ? Math.round(n).toLocaleString('en-US') : '—'

export const fmtMoneyExact = (n: number): string =>
  Number.isFinite(n) ? `$${Math.round(n).toLocaleString('en-US')}` : '—'

export const fmtPsf = (n: number | null): string =>
  n !== null && Number.isFinite(n) ? `$${n.toFixed(2)}` : '—'

export const pct = (part: number, whole: number): number =>
  whole > 0 ? (part / whole) * 100 : 0
