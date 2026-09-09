/** Quiet placeholders while the sheet fetch resolves — same layout as the loaded Overview. */
export function LoadingSkeleton() {
  return (
    <>
      <div className="kpi-band">
        {Array.from({ length: 6 }, (_, i) => (
          <div className="kpi" key={i}>
            <div className="skeleton" style={{ height: 25, width: '60%' }} />
            <div className="skeleton" style={{ height: 9, width: '80%', marginTop: 8 }} />
            <div className="skeleton" style={{ height: 9, width: '50%', marginTop: 5 }} />
          </div>
        ))}
      </div>
      <div className="view">
        <div className="ov-grid">
          <div className="card" style={{ minHeight: 520 }}>
            <div className="card-hd">
              <span className="skeleton" style={{ height: 11, width: 140 }} />
            </div>
            <div className="skeleton" style={{ flex: 1, margin: 1 }} />
          </div>
          <div className="ov-rail">
            <div className="card card-pad" style={{ height: 220 }}>
              <div className="skeleton" style={{ height: 11, width: 130 }} />
              <div className="skeleton" style={{ flex: 1, marginTop: 14 }} />
            </div>
            <div className="card card-pad" style={{ flex: 1, minHeight: 280 }}>
              <div className="skeleton" style={{ height: 11, width: 150 }} />
              <div className="skeleton" style={{ flex: 1, marginTop: 14 }} />
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
