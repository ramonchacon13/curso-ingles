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

export default function PracticaVoz() {
  const { user } = useAuth()
  const isPremium = user?.is_premium || user?.role === 'admin' || user?.role === 'moderator'

  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm your English buddy 😊 Tap the mic and talk to me, or pick a phrase. Let's practice!" },
  ])
  const [listening, setListening] = useState(false)
  const [thinking, setThinking] = useState(false)
  const [textMode, setTextMode] = useState(false)
  const [text, setText] = useState('')
  const [supported, setSupported] = useState(true)

  const recRef = useRef(null)
  const endRef = useRef(null)
  const synthRef = useRef(null)

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
      if (transcript) send(transcript)
    }
    rec.onerror = () => setListening(false)
    rec.onend = () => setListening(false)
    recRef.current = rec
  }, [])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, thinking])

  const speak = (text) => {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'en-US'
    u.rate = 0.95
    window.speechSynthesis.speak(u)
  }

  const send = async (content) => {
    if (!content.trim() || thinking) return
    const next = [...messages, { role: 'user', content }]
    setMessages(next)
    setThinking(true)
    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }))
      const data = await aiApi.tutor(content, history)
      const reply = data.reply
      setMessages((m) => [...m, { role: 'assistant', content: reply }])
      speak(reply)
    } catch (err) {
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

  if (!isPremium) {
    return (
      <div className="voice-page">
        <div className="voice-lock">
          <Icon name="crown" size={42} />
          <h1>Práctica tu voz con IA</h1>
          <p>Conversa en inglés con tu tutor personal que <b>escucha y habla</b>. Aprende pronunciando, sin presión.</p>
          <a className="btn-primary" href="/membresia">Hazte premium</a>
        </div>
      </div>
    )
  }

  return (
    <div className="voice-page">
      <h1><Icon name="chat" size={26} /> Practica tu voz 🎙️</h1>
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

      {!supported && (
        <p className="voice-note">Tu navegador no soporta reconocimiento de voz; usa el teclado para practicar. 💬</p>
      )}
      {supported && (
        <button className="voice-toggle" onClick={() => setTextMode((t) => !t)}>
          {textMode ? '🎤 Usar micrófono' : '⌨️ Escribir en su lugar'}
        </button>
      )}
    </div>
  )
}
