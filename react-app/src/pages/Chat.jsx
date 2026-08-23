import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { getToken } from '../api.js'
import { chatApi } from '../api.js'
import Icon from '../components/Icon.jsx'
import EmojiPicker from '../components/EmojiPicker.jsx'

function nowTime() {
  return new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

const COMMUNITY_RULES = [
  'Respeta a todos. Sin insultos, acoso ni lenguaje ofensivo.',
  'Escribe en español o inglés; ayuda a practicar, no satures el chat.',
  'No spam, publicidad ni enlaces sospechosos.',
  'Cuida tu privacidad: no compartas datos personales.',
  'Los moderadores pueden eliminar mensajes que infrinjan estas normas.',
  'Si ves algo inapropiado, repórtalo al equipo.',
]

export default function Chat() {
  const { user } = useAuth()
  const isMod = user?.role === 'admin' || user?.role === 'moderator'
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [online, setOnline] = useState(0)
  const [connected, setConnected] = useState(false)
  const [showRules, setShowRules] = useState(true)
  const wsRef = useRef(null)
  const endRef = useRef(null)

  useEffect(() => {
    const token = getToken()
    if (!token) return
    const API_BASE = import.meta.env.VITE_API_URL || ''
    const wsBase = API_BASE
      ? API_BASE.replace(/^http/, 'ws')
      : `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}`
    let unmounted = false
    let timer = null
    const connect = () => {
      const ws = new WebSocket(`${wsBase}/api/chat/ws?token=${token}`)
      wsRef.current = ws
      ws.onopen = () => setConnected(true)
      ws.onclose = () => {
        setConnected(false)
        if (!unmounted) timer = setTimeout(connect, 2000)
      }
      ws.onmessage = (e) => {
        const data = JSON.parse(e.data)
        if (data.type === 'online') {
          setOnline(data.count)
        } else if (data.type === 'delete') {
          setMessages((m) => m.filter((x) => x.id !== data.id))
        } else if (data.type === 'msg') {
          setMessages((m) => [...m, {
            id: data.id,
            user_id: data.user_id,
            user: data.user,
            role: data.role,
            content: data.content,
            time: data.time ? data.time.slice(11, 16) : nowTime(),
            mine: data.user_id === user?.id,
          }])
        }
      }
    }
    connect()
    return () => {
      unmounted = true
      if (timer) clearTimeout(timer)
      wsRef.current?.close()
    }
  }, [user])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = (e) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || !wsRef.current || wsRef.current.readyState !== 1) return
    wsRef.current.send(text)
    setInput('')
  }

  const removeMessage = async (id) => {
    try {
      await chatApi.deleteMessage(id)
    } catch (err) {
      alert(err.message || 'No se pudo eliminar el mensaje')
    }
  }

  const roleLabel = (role) =>
    role === 'admin' ? 'Admin' : role === 'moderator' ? 'Mod' : null

  return (
    <div className="chat-page">
      <h1><Icon name="chat" size={26} /> Chat de la comunidad</h1>
      <p className="chat-sub">
        <span className={`status-dot ${connected ? 'on' : 'off'}`} />
        {connected ? 'En línea' : 'Conectando...'} ·
        {' '}{online} usuario(s) en el chat
        {isMod && <span className="mod-flag"><Icon name="shield" size={14} /> Moderador</span>}
      </p>

      <div className="rules-panel">
        <button className="rules-head" onClick={() => setShowRules((s) => !s)}>
          <Icon name="info" size={18} />
          <strong>Normas de la comunidad</strong>
          <span className="rules-toggle">{showRules ? 'Ocultar' : 'Ver'}</span>
        </button>
        {showRules && (
          <ul className="rules-list">
            {COMMUNITY_RULES.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        )}
      </div>

      <div className="chat-window">
        {messages.length === 0 && <div className="chat-empty">Sé el primero en saludar en el chat.</div>}
        {messages.map((m) => {
          const label = roleLabel(m.role)
          return (
            <div key={m.id} className={`bubble ${m.mine ? 'user' : 'assistant'}`}>
              <div className="bubble-head">
                <strong>{m.user}</strong>
                {label && <span className={`role-badge ${m.role}`}>{label}</span>}
                <span className="bubble-time">{m.time}</span>
                {isMod && (
                  <button
                    className="bubble-del"
                    title="Eliminar mensaje"
                    onClick={() => removeMessage(m.id)}
                  >
                    <Icon name="trash" size={14} />
                  </button>
                )}
              </div>
              {m.content}
            </div>
          )
        })}
        <div ref={endRef} />
      </div>

      <form onSubmit={send} className="chat-form">
        <EmojiPicker onSelect={(e) => setInput((prev) => prev + e)} />
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Escribe un mensaje..."
        />
        <button className="btn-primary" disabled={!connected}>Enviar</button>
      </form>
    </div>
  )
}
