import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { useEffect, useState } from 'react'
import { api } from '../api.js'
import Icon from '../components/Icon.jsx'

export default function Landing() {
  const { user } = useAuth()
  const [niveles, setNiveles] = useState([])

  useEffect(() => {
    api.get('/niveles').then(setNiveles).catch(() => {})
  }, [])

  return (
    <div className="landing">
      <section className="hero">
        <h1>Aprende <span>inglés</span> gratis, a tu ritmo</h1>
        <p>Cursos por niveles, un chat en vivo con la comunidad, tests para medir tu progreso y tu propio panel de avance.</p>
        <div className="hero-actions">
          {user ? (
            <Link to="/dashboard" className="btn-primary">Ir a mi panel</Link>
          ) : (
            <>
              <Link to="/register" className="btn-primary">Empieza gratis</Link>
              <Link to="/login" className="btn-secondary">Ya tengo cuenta</Link>
            </>
          )}
        </div>
        <div className="hero-badges">
          <span><Icon name="book" size={18} /> 6 niveles (A1–C2)</span>
          <span><Icon name="chat" size={18} /> Chat en vivo</span>
          <span><Icon name="check" size={18} /> Tests y progreso</span>
        </div>
      </section>

      <section className="features">
        <div className="feature-card">
          <h3><Icon name="book" size={20} /> Cursos por niveles</h3>
          <p>De A1 a C2, con lecciones claras y progresivas desde cero.</p>
        </div>
        <div className="feature-card">
          <h3><Icon name="chat" size={20} /> Chat de la comunidad</h3>
          <p>Conversa en tiempo real con otros estudiantes que también aprenden.</p>
        </div>
        <div className="feature-card">
          <h3><Icon name="check" size={20} /> Tests y progreso</h3>
          <p>Comprueba tu nivel y sigue tu avance en tu panel personal.</p>
        </div>
      </section>

      <section>
        <h2 style={{ textAlign: 'center', color: 'var(--azul-osc)', marginBottom: 8 }}>¿Cómo funciona?</h2>
        <div className="steps">
          <div className="step"><div className="num">1</div><h3>Regístrate</h3><p>Crea tu cuenta gratis en segundos.</p></div>
          <div className="step"><div className="num">2</div><h3>Estudia</h3><p>Elige tu nivel y avanza con las lecciones.</p></div>
          <div className="step"><div className="num">3</div><h3>Practica</h3><p>Chat y tests para afianzar lo aprendido.</p></div>
        </div>
      </section>

      <section>
        <h2 style={{ textAlign: 'center', color: 'var(--azul-osc)', marginBottom: 8 }}>Niveles disponibles</h2>
        <div className="levels-preview">
          {niveles.map((n) => (
            <div key={n.code} className="lvl-chip">
              <b>{n.code}</b>
              <small>{n.name}</small>
            </div>
          ))}
        </div>
      </section>

      <section className="cta">
        <h2>¿List@ para empezar?</h2>
        <Link to={user ? "/dashboard" : "/register"} className="btn-primary">
          {user ? "Mi panel" : "Crear cuenta gratis"}
        </Link>
      </section>
    </div>
  )
}
