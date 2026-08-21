import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { api, userApi } from '../api.js'
import Icon from '../components/Icon.jsx'

export default function Dashboard() {
  const { user, refresh } = useAuth()
  const [niveles, setNiveles] = useState([])
  const [progreso, setProgreso] = useState(null)

  useEffect(() => {
    api.get('/niveles').then(setNiveles).catch(() => {})
    userApi.progreso().then(setProgreso).catch(() => {})
  }, [])

  return (
    <div className="dashboard">
      <h1>Hola, {user?.nombre}</h1>
      <div className="level-badge">Tu nivel: <strong>{user?.nivel}</strong></div>

      {progreso && (
        <div className="progress-card">
          <div className="progress-head">
            <span>Tu progreso</span>
            <strong>{progreso.porcentaje}% completado</strong>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progreso.porcentaje}%` }} />
          </div>
          <p className="muted">{progreso.completadas} de {progreso.total_lecciones} lecciones</p>
        </div>
      )}

      <div className="dash-actions">
        <Link to="/cursos" className="dash-card"><Icon name="book" size={22} /> Ver cursos</Link>
        <Link to="/chat" className="dash-card"><Icon name="chat" size={22} /> Chat de la comunidad</Link>
        <Link to="/tests" className="dash-card"><Icon name="check" size={22} /> Hacer un test</Link>
        <Link to="/perfil" className="dash-card"><Icon name="user" size={22} /> Mi perfil</Link>
        {!user?.is_premium && <Link to="/membresia" className="dash-card premium"><Icon name="star" size={22} /> Hacerse premium</Link>}
      </div>

      <h2>Niveles disponibles</h2>
      <div className="levels-grid">
        {niveles.map((n) => {
          const info = progreso?.by_level?.[n.code]
          return (
            <div key={n.code} className={`level-card ${n.code === user?.nivel ? 'active' : ''}`}>
              <span className="level-code">{n.code}</span>
              <h3>{n.name}</h3>
              <p>{n.description}</p>
              {info && (
                <div className="progress-bar small">
                  <div className="progress-fill" style={{ width: `${info.total ? (info.completadas / info.total * 100) : 0}%` }} />
                </div>
              )}
              <Link to="/cursos" className="btn-secondary">Explorar</Link>
            </div>
          )
        })}
      </div>
    </div>
  )
}
