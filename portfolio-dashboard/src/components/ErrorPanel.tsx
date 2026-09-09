import { config } from '../config'

/** Shown only when the sheet fetch failed AND there is no cached copy to fall back on. */
export function ErrorPanel({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="view">
      <div className="error-panel">
        <div className="error-title">Portfolio data unavailable</div>
        <div className="error-body">
          <p style={{ marginTop: 0 }}>
            The dashboard reads every lease from Google Sheets and has no cached copy yet, so
            there is nothing to display.
          </p>
          <p>
            <b>Reported error:</b> {error}
          </p>
          <p>Check the following, then retry:</p>
          <ul style={{ margin: '6px 0 0', paddingLeft: 18, lineHeight: 1.7 }}>
            <li>
              <code>VITE_SHEET_ID</code> is set{config.spreadsheetId ? '' : ' — it is currently empty'}
            </li>
            <li>
              The tab is named <code>{config.sheetName}</code>
            </li>
            <li>
              The sheet is shared (API key: “Anyone with the link · Viewer”; CSV fallback: File →
              Share → Publish to web)
            </li>
            <li>
              See <code>SETUP.md</code> for the full checklist
            </li>
          </ul>
          <button className="pill" style={{ marginTop: 14 }} onClick={onRetry}>
            Retry
          </button>
        </div>
      </div>
    </div>
  )
}
