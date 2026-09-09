import { useEffect, useMemo, useRef, useState } from 'react'
import { geoNaturalEarth1, geoPath } from 'd3-geo'
import { scaleSqrt } from 'd3-scale'
import { feature } from 'topojson-client'
import type { FeatureCollection, Geometry } from 'geojson'
import worldTopo from 'world-atlas/countries-110m.json'
import { C, REGION_COLORS, REGION_ORDER, colorFor } from '../../tokens'
import { fmtDate, fmtInt, fmtMoney } from '../../lib/format'
import type { Lease } from '../../types'
import { PropertyDetail } from './PropertyDetail'

/**
 * Real geometry only: Natural Earth countries (world-atlas 110m) projected with
 * geoNaturalEarth1. Antarctica is dropped and the extent is cropped to match.
 */
type CountryProps = { name?: string }

const world = feature(
  worldTopo as never,
  (worldTopo as unknown as { objects: { countries: unknown } }).objects.countries as never,
) as unknown as FeatureCollection<Geometry, CountryProps>

const land: FeatureCollection<Geometry, CountryProps> = {
  type: 'FeatureCollection',
  features: world.features.filter((f) => f.properties?.name !== 'Antarctica'),
}

interface Size {
  w: number
  h: number
}

interface HoverState {
  lease: Lease
  x: number
  y: number
}

export function WorldMap({ leases }: { leases: Lease[] }) {
  const wrapRef = useRef<HTMLDivElement>(null)
  const tipRef = useRef<HTMLDivElement>(null)
  const [size, setSize] = useState<Size>({ w: 0, h: 0 })
  const [hover, setHover] = useState<HoverState | null>(null)
  const [selected, setSelected] = useState<Lease | null>(null)

  useEffect(() => {
    const el = wrapRef.current
    if (!el) return
    const ro = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect
      setSize({ w: Math.round(width), h: Math.round(height) })
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  // Leases without coordinates can't be plotted; they still count everywhere else.
  const plottable = useMemo(
    () => leases.filter((l) => l.lat !== null && l.lng !== null),
    [leases],
  )

  const { pathD, dots } = useMemo(() => {
    if (size.w < 10 || size.h < 10) return { pathD: [] as string[], dots: [] as PlottedDot[] }
    const projection = geoNaturalEarth1().fitExtent(
      [
        [6, -size.h * 0.14],
        [size.w - 6, size.h * 1.02],
      ],
      land,
    )
    const path = geoPath(projection)
    const maxSf = Math.max(1, ...plottable.map((l) => l.sf))
    const r = scaleSqrt().domain([0, maxSf]).range([2.5, 17])

    // Larger dots first so small ones stay clickable on top.
    const plotted = [...plottable]
      .sort((a, b) => b.sf - a.sf)
      .flatMap((lease) => {
        const xy = projection([lease.lng as number, lease.lat as number])
        if (!xy) return []
        return [{ lease, cx: xy[0], cy: xy[1], r: r(lease.sf) }]
      })

    return {
      pathD: land.features.map((f) => path(f) ?? ''),
      dots: plotted,
    }
  }, [size, plottable])

  const onDotMove = (lease: Lease, e: React.MouseEvent) => {
    const rect = wrapRef.current?.getBoundingClientRect()
    if (!rect) return
    setHover({ lease, x: e.clientX - rect.left, y: e.clientY - rect.top })
  }

  // Keep the tooltip inside the card.
  const tipStyle = (): React.CSSProperties => {
    if (!hover) return { display: 'none' }
    const tw = tipRef.current?.offsetWidth ?? 200
    const th = tipRef.current?.offsetHeight ?? 70
    return {
      left: Math.max(6, Math.min(hover.x + 14, size.w - tw - 10)),
      top: Math.max(6, hover.y - 14 - th),
    }
  }

  const regionsPresent = useMemo(() => {
    const present = new Set(leases.map((l) => l.region))
    const ordered = REGION_ORDER.filter((r) => present.has(r)) as string[]
    const extra = [...present].filter((r) => r && !ordered.includes(r))
    return [...ordered, ...extra]
  }, [leases])

  return (
    <div
      className="map-wrap"
      ref={wrapRef}
      onClick={() => setSelected(null)}
      role="presentation"
    >
      <svg className="map-svg" width={size.w} height={size.h} aria-label="Global footprint map">
        <g>
          {pathD.map((d, i) => (
            <path key={i} d={d} fill={C.border} stroke="#fff" strokeWidth={0.6} />
          ))}
        </g>
        <g>
          {dots.map(({ lease, cx, cy, r }) => {
            const active = lease.status === 'Active'
            return (
              <circle
                key={lease.id}
                className="map-dot"
                cx={cx}
                cy={cy}
                r={r}
                fill={colorFor(REGION_COLORS, lease.region)}
                fillOpacity={0.78}
                stroke={active ? C.goldenrod : '#fff'}
                strokeWidth={active ? 2 : 1}
                onMouseMove={(e) => onDotMove(lease, e)}
                onMouseLeave={() => setHover(null)}
                onClick={(e) => {
                  e.stopPropagation()
                  setSelected(lease)
                  setHover(null)
                }}
              >
                <title>{`${lease.city}, ${lease.st}`}</title>
              </circle>
            )
          })}
        </g>
      </svg>

      {hover && (
        <div className="map-tip" ref={tipRef} style={tipStyle()}>
          <b>
            {hover.lease.city}, {hover.lease.st}
          </b>
          {hover.lease.addr}
          <br />
          {[hover.lease.seg, hover.lease.type, `${fmtInt(hover.lease.sf)} SF`]
            .filter(Boolean)
            .join(' · ')}
          <br />
          AGR {fmtMoney(hover.lease.agr)} · Expires{' '}
          <span className="gold">{fmtDate(hover.lease.expDate)}</span>
          {hover.lease.status === 'Active' && (
            <>
              <br />
              <span className="gold">ACTIVE TRANSACTION</span>
            </>
          )}
        </div>
      )}

      <div className="map-legend">
        {regionsPresent.map((r) => (
          <span key={r}>
            <i style={{ background: colorFor(REGION_COLORS, r) }} />
            {r}
          </span>
        ))}
      </div>

      {selected && <PropertyDetail lease={selected} onClose={() => setSelected(null)} />}
    </div>
  )
}

interface PlottedDot {
  lease: Lease
  cx: number
  cy: number
  r: number
}
