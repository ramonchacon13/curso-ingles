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
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [openTips, setOpenTips] = useState({})

  const toggleTip = (i) => setOpenTips((t) => ({ ...t, [i]: !t[i] }))

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
    const data = await api.get(`/niveles/${code}/tests`)
    setTests(data)
  }

  const openTest = (t) => {
    setActive(t)
    setAnswers({})
    setResult(null)
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

      {active && (
        <div className="test-active">
          <button className="back-link" onClick={() => setActive(null)}>← Volver</button>
          <h2>{active.title}</h2>
          {active.questions.map((q, i) => {
            const answered = answers[i] !== undefined
            const isCorrect = answered && answers[i] === q.correct
            return (
              <div key={q.id} className="question">
                <p className="question-prompt">
                  <span className="q-number">{i + 1}</span> {q.prompt}
                  {!isSpanish(q.prompt) && <SpeakButton text={q.prompt} />}
                </p>
                {q.options.map((opt, oi) => (
                  <label
                    key={oi}
                    className={`option ${answered ? (oi === q.correct ? 'correct' : answers[i] === oi ? 'wrong' : '') : ''}`}
                  >
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
                <div className="question-feedback">
                  {answered ? (
                    <>
                      <span className={isCorrect ? 'ok' : 'bad'}>{isCorrect ? '✓ Correcto' : '✗ Incorrecto'}</span>
                      {q.explanation && <p className="theory-tip">💡 {q.explanation}</p>}
                    </>
                  ) : q.explanation ? (
                    <>
                      <button type="button" className="tip-toggle" onClick={() => toggleTip(i)}>
                        💡 {openTips[i] ? 'Ocultar tip de teoría' : 'Ver tip de teoría'}
                      </button>
                      {openTips[i] && <p className="theory-tip">💡 {q.explanation}</p>}
                    </>
                  ) : null}
                </div>
              </div>
            )
          })}
          {error && <div className="alert-error">{error}</div>}
          <button className="btn-primary" onClick={submit}>Enviar test</button>

          {result && (
            <div className="test-result">
              <h3>Resultado: {result.score} / {result.total}</h3>
              <p>{Math.round((result.score / result.total) * 100)}% de aciertos</p>
              {result.nivel_actualizado ? (
                <div className="alert ok">¡Felicidades! Tu nivel se actualizó a <strong>{result.nivel}</strong>.</div>
              ) : (
                <p className="muted">Acierta al menos el 60% para que tu nivel se actualice automáticamente.</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
