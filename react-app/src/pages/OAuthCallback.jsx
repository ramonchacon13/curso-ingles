import { useEffect, useState } from 'react'
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
  const [status, setStatus] = useState('Procesando…')
  const [err, setErr] = useState(null)

  useEffect(() => {
    try {
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
      setStatus('Guardando sesión…')
      setSession(token, {})
      setStatus('Decodificando usuario…')
      const sub = decodeSub(token)
      setStatus('Usuario: ' + sub)
      if (sub) setUser({ id: sub })
      setStatus('Navegando al dashboard…')
      navigate('/dashboard', { replace: true })
      setStatus('Refrescando datos…')
      refresh().catch(() => {})
    } catch (e) {
      console.error('OAuthCallback error', e)
      setErr(e && e.message ? e.message : 'Error desconocido')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (err) {
    return (
      <div className="auth-page" style={{ padding: 24 }}>
        <p>Error al iniciar sesión con Google:</p>
        <pre style={{ whiteSpace: 'pre-wrap', color: '#f87171' }}>{err}</pre>
        <button className="btn-primary" onClick={() => navigate('/login')}>
          Volver al inicio de sesión
        </button>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <p>{status}</p>
    </div>
  )
}
