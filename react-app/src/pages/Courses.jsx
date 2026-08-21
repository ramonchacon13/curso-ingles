import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'

export default function Courses() {
  const [niveles, setNiveles] = useState([])
  const [selected, setSelected] = useState(null)
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/niveles').then((d) => { setNiveles(d); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const loadCourses = async (code) => {
    setSelected(code)
    const data = await api.get(`/niveles/${code}/cursos`)
    setCourses(data)
  }

  return (
    <div className="courses">
      <h1>Cursos</h1>
      {loading && <p className="muted">Cargando niveles...</p>}
      <div className="level-tabs">
        {niveles.map((n) => (
          <button
            key={n.code}
            className={`tab ${selected === n.code ? 'active' : ''}`}
            onClick={() => loadCourses(n.code)}
          >
            {n.code} · {n.name}
          </button>
        ))}
      </div>

      {selected && (
        <div className="courses-list">
          {courses.map((c) => (
            <div key={c.id} className="course-block">
              <h2>{c.title}</h2>
              <p>{c.description}</p>
              <ul className="lesson-list">
                {c.lessons.map((l) => (
                  <li key={l.id}>
                    <Link to={`/lecciones/${l.id}`}>
                      {l.title} {l.is_premium && <span className="premium-tag">PREMIUM</span>}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
