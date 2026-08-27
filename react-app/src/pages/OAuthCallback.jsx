import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { setSession } from '../api.js'

function decodeSub(token) {
  try {
    const p = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    const json = JSON.parse(atob(p))
    return json.sub || null
  } catch {
    return null
  }
}

export default function OAuthCallback() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const { refresh, setUser } = useAuth()

  useEffect(() => {
    const token = params.get('token')
    const error = params.get('error')
    if (error) {
      navigate(`/login?error=${error}`, { replace: true })
      return
    }
    if (!token) {
      navigate('/login', { replace: true })
      return
    }
    setSession(token, {})
    const sub = decodeSub(token)
    if (sub) setUser({ id: sub })
    navigate('/dashboard', { replace: true })
    refresh().catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="auth-page">
      <p>Entrando…</p>
    </div>
  )
}
