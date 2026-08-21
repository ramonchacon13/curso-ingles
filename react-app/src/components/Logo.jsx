export default function Logo({ size = 32 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" role="img" aria-label="CursoInglés">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#1f6feb" />
          <stop offset="1" stopColor="#18b663" />
        </linearGradient>
      </defs>
      <rect width="64" height="64" rx="14" fill="url(#g)" />
      <path d="M16 20h32a4 4 0 0 1 4 4v14a4 4 0 0 1-4 4H28l-10 8v-8h-2a4 4 0 0 1-4-4V24a4 4 0 0 1 4-4z" fill="#fff" opacity="0.95"/>
      <text x="32" y="38" font-size="16" font-family="Arial" font-weight="bold" fill="#1f6feb" text-anchor="middle">EN</text>
    </svg>
  )
}
