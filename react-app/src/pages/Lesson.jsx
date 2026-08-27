import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { api, userApi } from '../api.js'
import Icon from '../components/Icon.jsx'
import SpeakButton from '../components/SpeakButton.jsx'

const SPANISH_MARKERS = [
  'él', 'tú', 'ella', 'eso', 'nosotros', 'ellos', 'verbo', 'sustantivo',
  'adjetivo', 'negativo', 'pregunta', 'ejemplo', 'traducción', 'nacionalidad',
  'significa', 'usamos', 'cuando', 'donde', 'comer', 'beber', 'dormir',
  'hablar', 'casa', 'libro', 'agua', 'muy', 'bien', 'pero', 'como', 'está',
  'estan', 'son', ' la ', ' el ', ' los ', ' las ', ' una ', ' un ', ' de ',
  ' y ', ' con ', ' para ', ' por ', ' su ', ' se ',
]

function lessonAudioText(content) {
  if (!content) return ''
  const labelRe = /^(ejemplo|ej|negativo|positivo|pregunta|nota|tip|traducci[oó]n|respuesta)\s*[:\-]\s*/i
  return content
    .split('\n')
    .map((l) => l.replace(labelRe, ''))
    .filter((l) => {
      const t = l.toLowerCase()
      if (!t.trim()) return false
      if (t.includes(' = ')) return false
      return !SPANISH_MARKERS.some((w) => t.includes(w))
    })
    .join(' ')
}

export default function Lesson() {
  const { id } = useParams()
  const navigate = useNavigate()
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
      if (r.completada && lesson?.level_code) {
        navigate(`/tests?nivel=${lesson.level_code}`)
      }
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
      <div className="lesson-audio">
        <SpeakButton
          text={lessonAudioText(lesson.content)}
          label="Escuchar ejemplos en inglés"
          size={18}
        />
        <span className="muted small">Escucha los ejemplos en inglés de la lección</span>
      </div>
      <div className="lesson-content">{lesson.content}</div>
      <button
        className={`btn-complete ${completada ? 'done' : ''}`}
        onClick={toggle}
        disabled={busy}
      >
        <Icon name={completada ? 'check' : 'circle'} size={18} />
        {completada ? 'Lección completada' : 'Marcar como completada'}
      </button>
      {lesson.level_code && (
        <Link to={`/tests?nivel=${lesson.level_code}`} className="btn-secondary" style={{ marginLeft: 12 }}>
          Ir a las preguntas
        </Link>
      )}
    </div>
  )
}
