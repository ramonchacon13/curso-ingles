import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api.js'
import SpeakButton from '../components/SpeakButton.jsx'
import { isSpanish } from '../lib/lang.js'

export default function Tests() {
  const { refresh, user } = useAuth()
  const [searchParams] = useSearchParams()
  const [niveles, setNiveles] = useState([])
  const [selected, setSelected] = useState(null)
  const [tests, setTests] = useState([])
  const [active, setActive] = useState(null)
  const [answers, setAnswers] = useState({})
  const [phase, setPhase] = useState('taking')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/niveles').then((d) => {
      setNiveles(d); setLoading(false)
      const code = searchParams.get('nivel') || (user && user.nivel) || d[0]?.code
      if (code) loadTests(code)
    }).catch(() => setLoading(false))
  }, [])

  const loadTests = async (code) => {
    setSelected(code)
    setActive(null)
    setResult(null)
    setAnswers({})
    setPhase('taking')
    const data = await api.get(`/niveles/${code}/tests`)
    setTests(data)
  }

  const openTest = (t) => {
    setActive(t)
    setAnswers({})
    setResult(null)
    setPhase('taking')
  }

  const submit = async () => {
    setError('')
    const ans = active.questions.map((_, i) => answers[i])
    if (ans.some((a) => a === undefined)) {
      setError('Responde todas las preguntas')
      return
    }
    try {
      const r = await api.post('/tests/submit', { test_id: active.id, answers: ans })
      setResult(r)
      setPhase('result')
      if (r.nivel_actualizado) await refresh()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="tests">
      <h1>Tests de nivel</h1>
      {loading && <p className="muted">Cargando niveles...</p>}
      <div className="level-tabs">
        {niveles.map((n) => (
          <button key={n.code} className={`tab ${selected === n.code ? 'active' : ''}`} onClick={() => loadTests(n.code)}>
            {n.code}
          </button>
        ))}
      </div>

      {selected && !active && (
        <div className="tests-list">
          {tests.length === 0 && <p>No hay tests para este nivel todavía.</p>}
          {tests.map((t) => (
            <button key={t.id} className="test-card" onClick={() => openTest(t)}>
              {t.title} ({t.questions.length} preguntas)
            </button>
          ))}
        </div>
      )}

      {active && phase === 'taking' && (
        <div className="test-active">
          <button className="back-link" onClick={() => setActive(null)}>← Volver</button>
          <h2>{active.title}</h2>
          <p className="muted">Responde todas las preguntas. No sabrás si están bien hasta el final.</p>
          {active.questions.map((q, i) => (
            <div key={q.id} className="question">
              <p className="question-prompt">
                <span className="q-number">{i + 1}</span> {q.prompt}
                {!isSpanish(q.prompt) && <SpeakButton text={q.prompt} />}
              </p>
              {q.options.map((opt, oi) => (
                <label key={oi} className={`option ${answers[i] === oi ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name={`q-${i}`}
                    checked={answers[i] === oi}
                    onChange={() => setAnswers((a) => ({ ...a, [i]: oi }))}
                  />
                  {opt}
                  {!isSpanish(opt) && <SpeakButton text={opt} size={14} />}
                </label>
              ))}
            </div>
          ))}
          {error && <div className="alert-error">{error}</div>}
          <button className="btn-primary" onClick={submit}>Terminar y ver resultado</button>
        </div>
      )}

      {active && phase === 'result' && result && (
        <div className="test-active">
          <button className="back-link" onClick={() => setActive(null)}>← Volver a los tests</button>
          <h2>Resultado: {result.score} / {result.total}</h2>
          <p className="muted">{Math.round((result.score / result.total) * 100)}% de aciertos</p>
          {result.nivel_actualizado ? (
            <div className="alert ok">¡Felicidades! Tu nivel se actualizó a <strong>{result.nivel}</strong>.</div>
          ) : (
            <p className="muted">Acierta al menos el 60% para que tu nivel se actualice automáticamente.</p>
          )}

          <h3 className="review-title">Corrección y aprendizaje</h3>
          <p className="muted">Revisa cada pregunta, tu respuesta y la correcta. Lee el tip para reforzar.</p>
          {active.questions.map((q, i) => {
            const chosen = answers[i]
            const ok = chosen === q.correct
            return (
              <div key={q.id} className={`review-card ${ok ? 'good' : 'bad'}`}>
                <p className="question-prompt">
                  <span className="q-number">{i + 1}</span> {q.prompt}
                  {!isSpanish(q.prompt) && <SpeakButton text={q.prompt} />}
                </p>
                <p className={ok ? 'ok' : 'bad'}>
                  {ok ? '✓ Tu respuesta fue correcta' : '✗ Tu respuesta fue incorrecta'}
                </p>
                <p className="review-answer">
                  <strong>Tu respuesta:</strong> {q.options[chosen]}
                  {!isSpanish(q.options[chosen]) && <SpeakButton text={q.options[chosen]} size={14} />}
                </p>
                <p className="review-answer">
                  <strong>Respuesta correcta:</strong> {q.options[q.correct]}
                  {!isSpanish(q.options[q.correct]) && <SpeakButton text={q.options[q.correct]} size={14} />}
                </p>
                {q.explanation && <p className="theory-tip">💡 {q.explanation}</p>}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
