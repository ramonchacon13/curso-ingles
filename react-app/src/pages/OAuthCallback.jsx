import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { setSession } from '../api.js'

export default function OAuthCallback() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const { refresh } = useAuth()

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
