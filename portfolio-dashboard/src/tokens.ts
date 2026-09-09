/** Cresa design tokens. Radius is 0 everywhere by brand rule — there is no radius token. */
export const C = {
  midnight: '#001E5A',
  navyHover: '#14316B',
  goldenrod: '#FFB600',
  stadiumBlue: '#243E8C',
  brightBlue: '#0056DA',
  warmOrange: '#FF8200',
  darkGray: '#595959',
  muted: '#8A93A8',
  body: '#1a1a1a',
  bodySoft: '#333',
  border: '#E6E6E6',
  hairline: '#EEF0F4',
  pageBg: '#F4F5F8',
  zebra: '#FAFBFD',
  hoverWash: '#F4F7FC',
  danger: '#C93B3B',
  warn: '#B54708',
  ok: '#1B8F6A',
  paleGray: '#C5CBD6',
  white: '#fff',
} as const

export const REGION_ORDER = [
  'West',
  'Southeast',
  'South Central',
  'Northeast',
  'Canada',
  'International',
] as const

export const REGION_COLORS: Record<string, string> = {
  West: C.brightBlue,
  Southeast: C.warmOrange,
  'South Central': C.midnight,
  Northeast: C.stadiumBlue,
  Canada: C.darkGray,
  International: C.goldenrod,
}

export const SEGMENT_COLORS: Record<string, string> = {
  Forensics: C.midnight,
  BES: C.stadiumBlue,
  'Corp/Forensics': C.brightBlue,
  APAC: C.goldenrod,
  EMEA: C.warmOrange,
  'Life Sciences': C.darkGray,
  'BES/Forensics': C.muted,
  Corporate: C.paleGray,
}

export const PROPERTY_TYPE_COLORS: Record<string, string> = {
  Flex: C.brightBlue,
  Office: C.midnight,
  Warehouse: C.warmOrange,
  'Exec Suite': C.goldenrod,
}

/** Falls back to pale gray so an unexpected sheet value still renders. */
export const colorFor = (map: Record<string, string>, key: string): string =>
  map[key] ?? C.paleGray
