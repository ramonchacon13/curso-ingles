import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [nombre, setNombre] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(nombre, email, password)
      navigate('/login')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <h1>Crear cuenta</h1>
      {error && <div className="alert-error">{error}</div>}
      <form onSubmit={submit} className="auth-form">
        <label>Nombre</label>
        <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
        <label>Correo</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label>Contraseña</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={4} />
        <button className="btn-primary" disabled={loading}>{loading ? 'Creando...' : 'Registrarme'}</button>
      </form>
      <p className="auth-switch">¿Ya tienes cuenta? <Link to="/login">Entrar</Link></p>
    </div>
  )
}
