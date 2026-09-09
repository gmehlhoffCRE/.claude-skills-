import type { CSSProperties, ReactNode } from 'react'

interface CardProps {
  title?: string
  hint?: ReactNode
  children: ReactNode
  /** Header/body padding preset: 'pad' puts the title inline with the body. */
  variant?: 'header' | 'pad'
  style?: CSSProperties
  bodyStyle?: CSSProperties
}

/** White card, 1px border, square corners — the shell every panel uses. */
export function Card({ title, hint, children, variant = 'header', style, bodyStyle }: CardProps) {
  if (variant === 'pad') {
    return (
      <section className="card card-pad" style={style}>
        {title && (
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 10 }}>
            <h2 className="card-title">{title}</h2>
            {hint && <span className="card-hint">{hint}</span>}
          </div>
        )}
        {children}
      </section>
    )
  }
  return (
    <section className="card" style={style}>
      {(title || hint) && (
        <div className="card-hd">
          {title && <h2 className="card-title">{title}</h2>}
          {hint && <span className="card-hint">{hint}</span>}
        </div>
      )}
      <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0, ...bodyStyle }}>
        {children}
      </div>
    </section>
  )
}
