import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { userApi } from '../api.js'
import Icon from '../components/Icon.jsx'

const NIVELES = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

export default function Perfil() {
  const { user, setUser, refresh } = useAuth()
  const [nombre, setNombre] = useState(user?.nombre || '')
  const [nivel, setNivel] = useState(user?.nivel || 'A1')
  const [actual, setActual] = useState('')
  const [nueva, setNueva] = useState('')
  const [repetir, setRepetir] = useState('')
  const [progreso, setProgreso] = useState(null)
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  useEffect(() => {
    userApi.progreso().then(setProgreso).catch(() => {})
  }, [])

  const guardarPerfil = async (e) => {
    e.preventDefault()
    setMsg(''); setErr('')
    try {
      await userApi.updatePerfil({ nombre, email: undefined })
      await refresh()
      setMsg('Perfil actualizado.')
    } catch (e2) {
      setErr(e2.message)
    }
  }

  const guardarNivel = async (e) => {
    e.preventDefault()
    setMsg(''); setErr('')
    try {
      await userApi.updateNivel(nivel)
      await refresh()
      setMsg('Nivel actualizado.')
    } catch (e2) {
      setErr(e2.message)
    }
  }

  const cambiarPassword = async (e) => {
    e.preventDefault()
    setMsg(''); setErr('')
    if (nueva !== repetir) { setErr('Las contraseñas no coinciden.'); return }
    if (nueva.length < 4) { setErr('La contraseña es muy corta.'); return }
    try {
      await userApi.updatePassword({ actual, nueva })
      setActual(''); setNueva(''); setRepetir('')
      setMsg('Contraseña actualizada.')
    } catch (e2) {
      setErr(e2.message)
    }
  }

  return (
    <div className="page narrow">
      <h1><Icon name="user" size={26} /> Mi perfil</h1>
      {msg && <div className="alert ok">{msg}</div>}
      {err && <div className="alert error">{err}</div>}

      <section className="card">
        <h2>Datos personales</h2>
        <form onSubmit={guardarPerfil} className="form-col">
          <label>Nombre
            <input value={nombre} onChange={(e) => setNombre(e.target.value)} />
          </label>
          <label>Correo
            <input value={user?.email} disabled />
          </label>
          <button className="btn-primary" type="submit">Guardar nombre</button>
        </form>
      </section>

      <section className="card">
        <h2>Mi nivel</h2>
        <p className="muted">Tu nivel actual también se actualiza automáticamente al aprobar un test.</p>
        <form onSubmit={guardarNivel} className="form-row">
          <select value={nivel} onChange={(e) => setNivel(e.target.value)}>
            {NIVELES.map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
          <button className="btn-primary" type="submit">Cambiar nivel</button>
        </form>
      </section>

      <section className="card">
        <h2>Cambiar contraseña</h2>
        <form onSubmit={cambiarPassword} className="form-col">
          <label>Contraseña actual
            <input type="password" value={actual} onChange={(e) => setActual(e.target.value)} />
          </label>
          <label>Nueva contraseña
            <input type="password" value={nueva} onChange={(e) => setNueva(e.target.value)} />
          </label>
          <label>Repetir nueva contraseña
            <input type="password" value={repetir} onChange={(e) => setRepetir(e.target.value)} />
          </label>
          <button className="btn-primary" type="submit">Actualizar contraseña</button>
        </form>
      </section>

      <section className="card">
        <h2>Mi progreso</h2>
        {progreso && (
          <>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progreso.porcentaje}%` }} />
            </div>
            <p className="muted">{progreso.completadas} de {progreso.total_lecciones} lecciones completadas ({progreso.porcentaje}%)</p>
            <div className="progress-levels">
              {Object.entries(progreso.by_level).map(([code, info]) => (
                <div key={code} className="progress-level">
                  <span className="pl-code">{code}</span>
                  <span className="pl-count">{info.completadas}/{info.total}</span>
                  <div className="progress-bar small">
                    <div className="progress-fill" style={{ width: `${info.total ? (info.completadas / info.total * 100) : 0}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  )
}
