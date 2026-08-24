import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import GoogleButton from '../components/GoogleButton.jsx'

const OAUTH_ERRORS = {
  oauth: 'No pudimos iniciar sesión con Google. Intenta de nuevo.',
  oauth_disabled: 'El acceso con Google no está disponible ahora.',
  oauth_email: 'Tu correo de Google no está verificado.',
}

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(params.get('error') ? (OAUTH_ERRORS[params.get('error')] || 'Error con Google.') : '')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <h1>Entrar</h1>
      {error && <div className="alert-error">{error}</div>}
      <GoogleButton label="Entrar con Google" />
      <div className="auth-divider"><span>o con tu correo</span></div>
      <form onSubmit={submit} className="auth-form">
        <label>Correo</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label>Contraseña</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button className="btn-primary" disabled={loading}>{loading ? 'Entrando...' : 'Entrar'}</button>
      </form>
      <p className="auth-switch">¿No tienes cuenta? <a href="/register">Regístrate</a></p>
    </div>
  )
}
