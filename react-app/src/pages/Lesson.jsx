import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api, userApi } from '../api.js'
import Icon from '../components/Icon.jsx'

export default function Lesson() {
  const { id } = useParams()
  const [lesson, setLesson] = useState(null)
  const [error, setError] = useState('')
  const [locked, setLocked] = useState(false)
  const [completada, setCompletada] = useState(false)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    setLesson(null)
    setCompletada(false)
    setError('')
    api.get(`/lecciones/${id}`)
      .then(setLesson)
      .catch((err) => {
        if (err.message.includes('premium')) setLocked(true)
        else setError(err.message)
      })
    userApi.progreso()
      .then((p) => setCompletada(p.lessons_done.includes(Number(id))))
      .catch(() => {})
  }, [id])

  const toggle = async () => {
    setBusy(true)
    try {
      const r = await userApi.completarLeccion(id)
      setCompletada(r.completada)
    } catch {
    } finally {
      setBusy(false)
    }
  }

  if (locked) {
    return (
      <div className="auth-page">
        <h1>Lección premium</h1>
        <p>Esta lección es solo para miembros premium.</p>
        <Link to="/membresia" className="btn-primary">Hazte premium</Link>
      </div>
    )
  }

  if (error) return <div className="alert-error">{error}</div>
  if (!lesson) return <p>Cargando...</p>

  return (
    <div className="lesson-page">
      <Link to="/cursos" className="back-link">← Volver a cursos</Link>
      <h1>{lesson.title}</h1>
      <div className="lesson-content">{lesson.content}</div>
      <button
        className={`btn-complete ${completada ? 'done' : ''}`}
        onClick={toggle}
        disabled={busy}
      >
        <Icon name={completada ? 'check' : 'circle'} size={18} />
        {completada ? 'Lección completada' : 'Marcar como completada'}
      </button>
    </div>
  )
}
