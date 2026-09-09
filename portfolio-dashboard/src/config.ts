/**
 * Runtime configuration. Everything here comes from Vite env vars so the same
 * build can point at a different sheet without a code change.
 * See SETUP.md and .env.example.
 */
const env = import.meta.env

const bool = (v: unknown, fallback = false): boolean =>
  v === undefined || v === '' ? fallback : String(v).toLowerCase() === 'true'

const int = (v: unknown, fallback: number): number => {
  const n = Number(v)
  return Number.isFinite(n) ? n : fallback
}

export const config = {
  /** Google Sheets file ID (the long token in the sheet URL). */
  spreadsheetId: (env.VITE_SHEET_ID as string | undefined) ?? '',
  /** Tab name inside the spreadsheet. */
  sheetName: (env.VITE_SHEET_NAME as string | undefined) ?? 'Portfolio',
  /** Browser-key restricted API key for Sheets API v4. Optional — CSV fallback works without it. */
  apiKey: (env.VITE_SHEETS_API_KEY as string | undefined) ?? '',
  /** Numeric gid of the tab; only needed by the published-CSV fallback for non-first tabs. */
  sheetGid: (env.VITE_SHEET_GID as string | undefined) ?? '',
  /** Months ahead that count as "expiring soon". */
  expiringMonths: int(env.VITE_EXPIRING_MONTHS, 12),
  /** Months covered by the expiration runway timeline. */
  runwayMonths: int(env.VITE_RUNWAY_MONTHS, 66),
  /** Dev only: render the bundled sample fixture instead of calling the sheet. */
  useFixture: bool(env.VITE_USE_FIXTURE, false),
  /** Footer provenance line. */
  sourceLabel:
    (env.VITE_SOURCE_LABEL as string | undefined) ??
    'Rimkus Real Estate Portfolio Summary · Prepared by Cresa',
} as const

export const CACHE_KEY = 'rimkus-portfolio-cache-v1'

/** True when neither transport can be attempted. */
export const hasSheetConfig = (): boolean =>
  config.useFixture || Boolean(config.spreadsheetId)
