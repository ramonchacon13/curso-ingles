import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { aiApi } from '../api.js'
import Icon from '../components/Icon.jsx'

const SUGGESTIONS = [
  'Hello! How are you?',
  'Can you repeat that, please?',
  'What does this word mean?',
  'I am learning English.',
  'Thank you, teacher!',
]

const TARGET_PHRASES = [
  { en: 'Hello, my name is Alex', es: 'Hola, mi nombre es Alex' },
  { en: 'I would like a glass of water', es: 'Quisiera un vaso de agua' },
  { en: 'Where is the train station', es: '¿Dónde está la estación de tren?' },
  { en: 'I study English every day', es: 'Estudio inglés todos los días' },
  { en: 'The weather is very nice today', es: 'El clima está muy agradable hoy' },
  { en: 'Could you help me please', es: '¿Podría ayudarme por favor?' },
  { en: 'I am happy to meet you', es: 'Estoy feliz de conocerte' },
  { en: 'She sells sea shells by the sea', es: 'Trabalenguas: ella vende conchas marinas' },
  { en: 'Can I have the menu', es: '¿Puedo tener el menú?' },
  { en: 'I love learning new languages', es: 'Amo aprender nuevos idiomas' },
]

function clean(s) {
  return s.toLowerCase().replace(/[^a-z0-9\s]/gi, '').replace(/\s+/g, ' ').trim()
}

function scoreAttempt(target, said) {
  const tWords = clean(target).split(' ').filter(Boolean)
  const sWords = clean(said).split(' ').filter(Boolean)
  if (tWords.length === 0) return { score: 0, segs: [] }
  let matches = 0
  let sIdx = 0
  const segs = tWords.map((w) => {
    if (sIdx < sWords.length && sWords[sIdx] === w) {
      matches++
      sIdx++
      return { w, ok: true }
    }
    if (sIdx < sWords.length) sIdx++
    return { w, ok: false }
  })
  const score = Math.round((matches / tWords.length) * 100)
  return { score, segs }
}

function tierMessage(score) {
  if (score >= 90) return { text: '¡Perfecto! 🎉', cls: 'great' }
  if (score >= 70) return { text: '¡Muy bien! 💪', cls: 'good' }
  if (score >= 50) return { text: 'Bien, sigue así 👍', cls: 'ok' }
  return { text: '¡Lo intentaste! Vuelve a probar 💡', cls: 'soft' }
}

export default function pickBestVoice(vs) {
  const prefs = ['natural', 'neural', 'online', 'aria', 'samantha', 'google us english', 'zira', 'david', 'daniel']
  for (const p of prefs) {
    const found = vs.find((v) => v.name.toLowerCase().includes(p))
    if (found) return found
  }
  return vs[0]
}

function PracticaVoz() {
  const { user } = useAuth()
  const isPremium = user?.is_premium || user?.role === 'admin' || user?.role === 'moderator'

  const [mode, setMode] = useState('chat') // 'chat' | 'repeat'
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm your English buddy 😊 Tap the mic and talk to me, or pick a phrase. Let's practice!" },
  ])
  const [listening, setListening] = useState(false)
  const [thinking, setThinking] = useState(false)
  const [textMode, setTextMode] = useState(false)
  const [text, setText] = useState('')
  const [supported, setSupported] = useState(true)
  const [voices, setVoices] = useState([])
  const [voiceURI, setVoiceURI] = useState('')

  useEffect(() => {
    const loadVoices = () => {
      const vs = window.speechSynthesis.getVoices().filter((v) => v.lang && v.lang.toLowerCase().startsWith('en'))
      setVoices(vs)
      if (!voiceURI && vs.length) setVoiceURI(pickBestVoice(vs).voiceURI)
    }
    loadVoices()
    window.speechSynthesis.onvoiceschanged = loadVoices
    return () => { window.speechSynthesis.onvoiceschanged = null }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const [phraseIdx, setPhraseIdx] = useState(0)
  const [result, setResult] = useState(null) // {score, segs}

  const recRef = useRef(null)
  const endRef = useRef(null)
  const messagesRef = useRef(messages)
  useEffect(() => { messagesRef.current = messages }, [messages])

  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) {
      setSupported(false)
      setTextMode(true)
      return
    }
    const rec = new SR()
    rec.lang = 'en-US'
    rec.interimResults = false
    rec.maxAlternatives = 1
    rec.onresult = (e) => {
      const transcript = e.results[0][0].transcript.trim()
      setListening(false)
      if (!transcript) {
        if (mode === 'chat') {
          setMessages((m) => [...m, { role: 'assistant', content: 'No te entendí bien, ¿puedes repetir? 💡' }])
        }
        return
      }
      if (mode === 'repeat') {
        const r = scoreAttempt(TARGET_PHRASES[phraseIdx].en, transcript)
        setResult(r)
        if (r.score >= 70) speak(TARGET_PHRASES[phraseIdx].en)
      } else {
        send(transcript)
      }
    }
    rec.onerror = (e) => {
      setListening(false)
      if (e.error === 'no-speech' && mode === 'chat') {
        setMessages((m) => [...m, { role: 'assistant', content: 'No te entendí bien, ¿puedes repetir? 💡' }])
      }
    }
    rec.onend = () => setListening(false)
    recRef.current = rec
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, phraseIdx])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, thinking])

  const speak = (txt) => {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(txt)
    u.lang = 'en-US'
    u.rate = 0.92
    u.pitch = 1
    const v = voices.find((x) => x.voiceURI === voiceURI) || (voices.length ? pickBestVoice(voices) : null)
    if (v) u.voice = v
    window.speechSynthesis.speak(u)
  }

  const send = async (content) => {
    if (!content.trim() || thinking) return
    setMessages((m) => [...m, { role: 'user', content }])
    setThinking(true)
    try {
      const history = messagesRef.current.map((m) => ({ role: m.role, content: m.content }))
      const data = await aiApi.tutor(content, history)
      setMessages((m) => [...m, { role: 'assistant', content: data.reply }])
      speak(data.reply)
    } catch {
      setMessages((m) => [...m, { role: 'assistant', content: '😊 Oops! I had a small problem. Try again in a moment.' }])
    } finally {
      setThinking(false)
      setText('')
    }
  }

  const toggleMic = () => {
    if (listening) {
      recRef.current?.stop()
      setListening(false)
      return
    }
    try {
      recRef.current?.start()
      setListening(true)
    } catch {
      setListening(false)
    }
  }

  const nextPhrase = () => {
    setResult(null)
    setPhraseIdx((i) => (i + 1) % TARGET_PHRASES.length)
  }

  if (!isPremium) {
    return (
      <div className="voice-page">
        <div className="voice-lock">
          <Icon name="crown" size={42} />
          <h1>Práctica tu voz con IA</h1>
          <p>Conversa en inglés con tu tutor personal que <b>escucha y habla</b>, y mejora tu pronunciación repitiendo frases. Aprende sin presión.</p>
          <a className="btn-primary" href="/membresia">Hazte premium</a>
        </div>
      </div>
    )
  }

  const phrase = TARGET_PHRASES[phraseIdx]

  return (
    <div className="voice-page">
      <h1><Icon name="chat" size={26} /> Practica tu voz 🎙️</h1>
      {voices.length > 0 && (
        <div className="voice-select">
          <label htmlFor="voice">Voz:</label>
          <select id="voice" value={voiceURI} onChange={(e) => setVoiceURI(e.target.value)}>
            {voices.map((v) => (
              <option key={v.voiceURI} value={v.voiceURI}>{v.name}</option>
            ))}
          </select>
        </div>
      )}

      <div className="mode-tabs">
        <button className={mode === 'chat' ? 'on' : ''} onClick={() => setMode('chat')}>💬 Conversar</button>
        <button className={mode === 'repeat' ? 'on' : ''} onClick={() => { setMode('repeat'); setResult(null) }}>🎯 Repite y practica</button>
      </div>

      {mode === 'chat' ? (
        <>
          <p className="voice-sub">Habla con tu tutor de inglés. Toca el micrófono y dile algo, o elige una frase. ¡Sin prisa, sin presión! 😊</p>
          <div className="voice-chat">
            {messages.map((m, i) => (
              <div key={i} className={`v-bubble ${m.role}`}>
                <div className="v-head">
                  {m.role === 'assistant' ? '🤖 Tutor' : '🗣️ Tú'}
                  {m.role === 'assistant' && (
                    <button className="v-speak" title="Escuchar" onClick={() => speak(m.content)}>
                      <Icon name="send" size={14} />
                    </button>
                  )}
                </div>
                {m.content}
              </div>
            ))}
            {thinking && <div className="v-bubble assistant"><div className="v-head">🤖 Tutor</div>Thinking… 💭</div>}
            <div ref={endRef} />
          </div>

          <div className="voice-suggest">
            {SUGGESTIONS.map((s) => (
              <button key={s} className="chip" onClick={() => send(s)}>{s}</button>
            ))}
          </div>

          {!textMode && (
            <button className={`mic-btn ${listening ? 'on' : ''}`} onClick={toggleMic}>
              <Icon name="send" size={26} />
              <span>{listening ? 'Escuchando… toca para parar' : 'Toca y habla'}</span>
            </button>
          )}
          {textMode && (
            <form className="voice-form" onSubmit={(e) => { e.preventDefault(); send(text) }}>
              <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Escribe en inglés…" />
              <button className="btn-primary" disabled={thinking || !text.trim()}>Enviar</button>
            </form>
          )}
          {!supported && <p className="voice-note">Tu navegador no soporta reconocimiento de voz; usa el teclado para practicar. 💬</p>}
          {supported && (
            <button className="voice-toggle" onClick={() => setTextMode((t) => !t)}>
              {textMode ? '🎤 Usar micrófono' : '⌨️ Escribir en su lugar'}
            </button>
          )}
        </>
      ) : (
        <div className="repeat-card">
          <p className="repeat-trans">{phrase.es}</p>
          <div className="target-phrase">{phrase.en}</div>
          <button className="v-speak big" title="Escuchar modelo" onClick={() => speak(phrase.en)}>
            <Icon name="send" size={16} /> Escuchar modelo
          </button>

          <button className={`mic-btn ${listening ? 'on' : ''}`} onClick={toggleMic}>
            <Icon name="send" size={26} />
            <span>{listening ? 'Repite la frase…' : 'Toca y repite la frase'}</span>
          </button>

          {result && (
            <div className="score-box">
              <div className={`score-ring ${tierMessage(result.score).cls}`}>{result.score}%</div>
              <p className="score-msg">{tierMessage(result.score).text}</p>
              <div className="word-line">
                {result.segs.map((s, i) => (
                  <span key={i} className={`word ${s.ok ? 'ok' : 'bad'}`}>{s.w}</span>
                ))}
              </div>
              <div className="repeat-actions">
                <button className="btn-ghost" onClick={() => setResult(null)}>Reintentar</button>
                <button className="btn-primary" onClick={nextPhrase}>Otra frase →</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
