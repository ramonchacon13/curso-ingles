const BG = '#0072CE'
const BG2 = '#18b663'
const BG3 = '#f4a300'
const BG4 = '#e23b3b'

function Glyph({ name }) {
  switch (name) {
    case 'people':
      return (
        <g fill="#fff">
          <circle cx="36" cy="40" r="11" />
          <path d="M20 72c0-11 7-18 16-18s16 7 16 18z" />
          <circle cx="66" cy="40" r="11" />
          <path d="M50 72c0-11 7-18 16-18s16 7 16 18z" />
        </g>
      )
    case 'coffee':
      return (
        <g fill="none" stroke="#fff" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M30 40h34v18a14 14 0 0 1-14 14H44a14 14 0 0 1-14-14z" fill="#fff" stroke="none" />
          <path d="M64 44h6a8 8 0 0 1 0 16h-6" />
          <path d="M38 28c-3 4 3 6 0 10M50 26c-3 4 3 6 0 10M62 28c-3 4 3 6 0 10" stroke="#fff" />
        </g>
      )
    case 'bag':
      return (
        <g fill="none" stroke="#fff" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M30 38h40l-4 36H34z" fill="#fff" stroke="none" />
          <path d="M40 38v-4a11 11 0 0 1 22 0v4" />
        </g>
      )
    case 'map':
      return (
        <g>
          <path d="M26 30l14-6 20 6 14-6v46l-14 6-20-6-14 6z" fill="#fff" stroke="#fff" strokeWidth="3" strokeLinejoin="round" />
          <path d="M40 24v46M74 24v46" stroke={BG} strokeWidth="3" />
          <path d="M58 44c0-7 6-7 6 0 0 5-6 11-6 11s-6-6-6-11c0-7 6-7 6 0z" fill={BG4} />
        </g>
      )
    case 'cross':
      return (
        <g fill="#fff">
          <rect x="44" y="28" width="12" height="44" rx="4" />
          <rect x="28" y="44" width="44" height="12" rx="4" />
        </g>
      )
    case 'laptop':
      return (
        <g>
          <rect x="28" y="30" width="44" height="28" rx="3" fill="#fff" />
          <rect x="34" y="36" width="32" height="16" rx="2" fill={BG} />
          <path d="M22 66h56l-4-8H26z" fill="#fff" />
        </g>
      )
    case 'muffin':
      return (
        <g>
          <path d="M34 46h32l-3 22a6 6 0 0 1-6 5H43a6 6 0 0 1-6-5z" fill="#fff" />
          <path d="M32 46c0-12 8-20 18-20s18 8 18 20c-6-6-10-4-12 0-3-5-8-5-12 0-3-4-7-3-12 0z" fill={BG3} />
        </g>
      )
    case 'card':
      return (
        <g>
          <rect x="26" y="36" width="48" height="30" rx="5" fill="#fff" />
          <rect x="26" y="44" width="48" height="7" fill={BG} />
          <rect x="32" y="56" width="14" height="5" rx="2" fill={BG2} />
        </g>
      )
    default:
      return <circle cx="50" cy="50" r="14" fill="#fff" />
  }
}

const COLORS = {
  people: BG, coffee: BG3, bag: BG2, map: BG, cross: BG4, laptop: BG, muffin: BG3, card: BG2,
}

export default function Illustration({ name, size = 72 }) {
  const color = COLORS[name] || BG
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" className="illu" aria-hidden="true">
      <circle cx="50" cy="50" r="47" fill={color} />
      <Glyph name={name} />
    </svg>
  )
}
