import { useCallback, useEffect, useState } from 'react'
import { config } from '../config'
import { FIXTURE_HEADER, FIXTURE_ROWS } from '../dev/fixture'
import { parseRows } from '../lib/parse'
import { fetchPortfolio, readCache, writeCache } from '../lib/sheets'
import type { DataEnvelope, LoadState } from '../types'

const fixtureEnvelope = (): DataEnvelope => {
  const { leases, warnings } = parseRows(FIXTURE_HEADER, FIXTURE_ROWS)
  return { leases, source: 'fixture', fetchedAt: new Date(), warnings }
}

/**
 * Loads the portfolio from the configured Google Sheet.
 * On failure it serves the last-good localStorage response and reports the error so the
 * header chip can go amber — the dashboard never renders hard-coded lease data.
 */
export function usePortfolioData(): { state: LoadState; refresh: () => void } {
  const [state, setState] = useState<LoadState>({ status: 'loading' })
  const [nonce, setNonce] = useState(0)

  useEffect(() => {
    let cancelled = false

    if (config.useFixture) {
      setState({ status: 'ready', data: fixtureEnvelope(), stale: false })
      return
    }

    setState({ status: 'loading' })
    fetchPortfolio()
      .then((data) => {
        if (cancelled) return
        writeCache(data)
        setState({ status: 'ready', data, stale: false })
      })
      .catch((err: unknown) => {
        if (cancelled) return
        const message = err instanceof Error ? err.message : String(err)
        const cached = readCache()
        setState(
          cached
            ? { status: 'ready', data: cached, stale: true, error: message }
            : { status: 'error', error: message },
        )
      })

    return () => {
      cancelled = true
    }
  }, [nonce])

  const refresh = useCallback(() => setNonce((n) => n + 1), [])
  return { state, refresh }
}
