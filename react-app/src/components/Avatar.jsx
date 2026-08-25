import { API_BASE } from '../api'

function initials(name) {
  if (!name) return '?'
  const parts = String(name).trim().split(/\s+/)
  const first = parts[0]?.[0] || ''
  const last = parts.length > 1 ? parts[parts.length - 1][0] : ''
  return (first + last).toUpperCase() || '?'
}

const COLORS = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b',
  '#10b981', '#06b6d4', '#3b82f6', '#a855f7', '#ef4444',
]

function colorFromId(id) {
  const n = Number(id) || 0
  return COLORS[n % COLORS.length]
}

export default function Avatar({ user, size = 40 }) {
  const kind = user?.avatar_kind || 'initials'
  const value = user?.avatar_value

  if (kind === 'image') {
    const src = value || `${API_BASE}/api/usuarios/${user.id}/avatar`
    return (
      <img
        src={src}
        width={size}
        height={size}
        alt=""
        style={{ borderRadius: '50%', objectFit: 'cover', display: 'inline-block', flexShrink: 0 }}
      />
    )
  }

  if (kind === 'emoji' && value) {
    return (
      <span
        style={{
          width: size, height: size, display: 'inline-flex',
          alignItems: 'center', justifyContent: 'center',
          fontSize: size * 0.55, background: '#1e293b',
          borderRadius: '50%', flexShrink: 0,
        }}
      >
        {value}
      </span>
    )
  }

  const ini = initials(user?.nombre)
  return (
    <span
      style={{
        width: size, height: size, display: 'inline-flex',
        alignItems: 'center', justifyContent: 'center',
        borderRadius: '50%', background: colorFromId(user?.id),
        color: '#fff', fontWeight: 700, fontSize: size * 0.4, flexShrink: 0,
      }}
    >
      {ini}
    </span>
  )
}
