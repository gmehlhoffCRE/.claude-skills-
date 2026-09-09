/** Canonical column headers in the client's "Real Estate Portfolio Summary" sheet. */
export const SHEET_COLUMNS = [
  'LEASE TYPE',
  'REGION',
  'TRANSACTION STATUS',
  'OPERATING SEGMENT',
  'LEASE CITY',
  'ST',
  'STREET ADDRESS',
  'PROPERTY TYPE',
  'SF',
  'LEASE EXP',
  'ANNUAL GROSS RENT ($US)',
  'CRESA NOTES',
  'LAT',
  'LNG',
] as const

export type SheetColumn = (typeof SHEET_COLUMNS)[number]

export type Region =
  | 'West'
  | 'Southeast'
  | 'South Central'
  | 'Northeast'
  | 'Canada'
  | 'International'

export type TransactionStatus = 'Active' | 'Inactive'

/** One lease, normalized from a sheet row. Extra columns are preserved in `extra`. */
export interface Lease {
  id: string
  leaseType: string
  region: string
  status: TransactionStatus
  seg: string
  city: string
  st: string
  addr: string
  type: string
  sf: number
  /** Raw LEASE EXP cell, kept for display/debugging ("MTM", a serial, an ISO string…). */
  expRaw: string
  /** Null when month-to-month or unparseable. */
  expDate: Date | null
  isMtm: boolean
  agr: number
  note: string
  lat: number | null
  lng: number | null
  /** Derived: annual gross rent per rentable square foot. */
  psf: number | null
  /** Any sheet column outside the canonical schema (roadmap: headcount, escalations…). */
  extra: Record<string, string>
}

export type DataSourceKind = 'sheets-api' | 'sheets-csv' | 'fixture' | 'cache'

export interface DataEnvelope {
  leases: Lease[]
  source: DataSourceKind
  fetchedAt: Date
  /** Rows the parser skipped, with a reason — surfaced in the console and status chip title. */
  warnings: string[]
}

export type LoadState =
  | { status: 'loading' }
  | { status: 'ready'; data: DataEnvelope; stale: false }
  | { status: 'ready'; data: DataEnvelope; stale: true; error: string }
  | { status: 'error'; error: string }

export type ViewKey = 'overview' | 'expirations' | 'pipeline' | 'table'
