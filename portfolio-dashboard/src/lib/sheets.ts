import { CACHE_KEY, config } from '../config'
import type { DataEnvelope, Lease } from '../types'
import { parseCsv, parseRows } from './parse'

/**
 * Data transport. Preference order:
 *   1. Sheets API v4 (needs VITE_SHEETS_API_KEY) — real API, typed values, quota-friendly.
 *   2. Published gviz CSV — no key needed, but the sheet must be published to the web.
 * On total failure the caller falls back to the localStorage cache.
 */

const apiUrl = (): string => {
  const range = encodeURIComponent(config.sheetName)
  return (
    `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(config.spreadsheetId)}` +
    `/values/${range}?majorDimension=ROWS&valueRenderOption=UNFORMATTED_VALUE` +
    `&dateTimeRenderOption=SERIAL_NUMBER&key=${encodeURIComponent(config.apiKey)}`
  )
}

const csvUrl = (): string => {
  const base = `https://docs.google.com/spreadsheets/d/${encodeURIComponent(
    config.spreadsheetId,
  )}/gviz/tq?tqx=out:csv`
  return config.sheetGid
    ? `${base}&gid=${encodeURIComponent(config.sheetGid)}`
    : `${base}&sheet=${encodeURIComponent(config.sheetName)}`
}

const REQUEST_TIMEOUT_MS = 15000

async function fetchWithTimeout(url: string): Promise<Response> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
  try {
    return await fetch(url, { signal: controller.signal, cache: 'no-store' })
  } finally {
    clearTimeout(timer)
  }
}

async function fetchViaApi(): Promise<DataEnvelope> {
  const res = await fetchWithTimeout(apiUrl())
  if (!res.ok) {
    const detail = await res.text().catch(() => '')
    throw new Error(
      `Sheets API ${res.status}: ${detail.slice(0, 200) || res.statusText}`,
    )
  }
  const json = (await res.json()) as { values?: unknown[][] }
  const values = json.values ?? []
  if (values.length < 2) throw new Error('Sheets API returned no data rows.')
  const [header, ...rows] = values
  const { leases, warnings } = parseRows(header.map(String), rows)
  return { leases, source: 'sheets-api', fetchedAt: new Date(), warnings }
}

async function fetchViaCsv(): Promise<DataEnvelope> {
  const res = await fetchWithTimeout(csvUrl())
  if (!res.ok) throw new Error(`Published CSV ${res.status}: ${res.statusText}`)
  const text = await res.text()
  if (text.trimStart().startsWith('<')) {
    throw new Error(
      'Published CSV returned HTML — the sheet is probably not published to the web.',
    )
  }
  const table = parseCsv(text)
  if (table.length < 2) throw new Error('Published CSV returned no data rows.')
  const [header, ...rows] = table
  const { leases, warnings } = parseRows(header, rows)
  return { leases, source: 'sheets-csv', fetchedAt: new Date(), warnings }
}

/** Tries API first when a key is configured, then the published-CSV fallback. */
export async function fetchPortfolio(): Promise<DataEnvelope> {
  if (!config.spreadsheetId) {
    throw new Error('VITE_SHEET_ID is not set — see SETUP.md.')
  }
  const errors: string[] = []
  if (config.apiKey) {
    try {
      return await fetchViaApi()
    } catch (err) {
      errors.push(err instanceof Error ? err.message : String(err))
    }
  }
  try {
    return await fetchViaCsv()
  } catch (err) {
    errors.push(err instanceof Error ? err.message : String(err))
  }
  throw new Error(errors.join(' | '))
}

/* ---------------------------------- cache ---------------------------------- */

interface CachedShape {
  fetchedAt: string
  source: string
  leases: (Omit<Lease, 'expDate'> & { expDate: string | null })[]
}

export function writeCache(env: DataEnvelope): void {
  try {
    const payload: CachedShape = {
      fetchedAt: env.fetchedAt.toISOString(),
      source: env.source,
      leases: env.leases.map((l) => ({ ...l, expDate: l.expDate ? l.expDate.toISOString() : null })),
    }
    localStorage.setItem(CACHE_KEY, JSON.stringify(payload))
  } catch {
    // Private mode / quota — caching is a nicety, never a hard failure.
  }
}

export function readCache(): DataEnvelope | null {
  try {
    const raw = localStorage.getItem(CACHE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as CachedShape
    if (!Array.isArray(parsed.leases) || parsed.leases.length === 0) return null
    return {
      leases: parsed.leases.map((l) => ({
        ...l,
        expDate: l.expDate ? new Date(l.expDate) : null,
      })),
      source: 'cache',
      fetchedAt: new Date(parsed.fetchedAt),
      warnings: [],
    }
  } catch {
    return null
  }
}
