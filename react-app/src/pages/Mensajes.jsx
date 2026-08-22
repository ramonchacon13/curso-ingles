import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { getToken, api } from '../api.js'
import Icon from '../components/Icon.jsx'
import EmojiPicker from '../components/EmojiPicker.jsx'

function initials(name) {
  return name.split(' ').map((p) => p[0]).slice(0, 2).join('').toUpperCase()
}
function nowTime() {
  return new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

export default function Mensajes() {
  const { user } = useAuth()
  const [contacts, setContacts] = useState([])
  const [peer, setPeer] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [connected, setConnected] = useState(false)
  const [peerOnline, setPeerOnline] = useState(false)
  const wsRef = useRef(null)
  const endRef = useRef(null)

  useEffect(() => {
    api.get('/usuarios').then(setContacts).catch(() => {})
  }, [])

  useEffect(() => {
    if (!peer) return
    const token = getToken()
    const API_BASE = import.meta.env.VITE_API_URL || ''
    const wsBase = API_BASE
      ? API_BASE.replace(/^http/, 'ws')
      : `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}`
    let unmounted = false
    let timer = null
    const connect = () => {
      const ws = new WebSocket(`${wsBase}/api/chat/private/ws?token=${token}&peer=${peer.id}`)
      wsRef.current = ws
      setMessages([])
      setPeerOnline(false)
      ws.onopen = () => setConnected(true)
      ws.onclose = () => {
        setConnected(false)
        if (!unmounted) timer = setTimeout(connect, 2000)
      }
      ws.onmessage = (e) => {
        const d = JSON.parse(e.data)
        if (d.type === 'online') {
          if (d.peer === user.id) setPeerOnline(d.online)
          return
        }
        if (d.type === 'msg') {
          setMessages((m) => [...m, { from: d.from, content: d.content, mine: d.from === user.id, time: nowTime() }])
        }
      }
    }
    connect()
    return () => {
      unmounted = true
      if (timer) clearTimeout(timer)
      wsRef.current?.close()
    }
  }, [peer, user])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = (e) => {
    e.preventDefault()
    const t = input.trim()
    if (!t || !wsRef.current || wsRef.current.readyState !== 1) return
    wsRef.current.send(t)
    setInput('')
  }

  return (
    <div className="mensajes">
      <h1 className="mensajes-title">Mensajes privados</h1>
      <div className="msg-layout">
        <aside className="msg-sidebar">
          <div className="msg-sidebar-head">Personas</div>
          {contacts.length === 0 && <p className="muted" style={{ padding: '12px' }}>No hay otros usuarios todavía.</p>}
          <div className="msg-contacts">
            {contacts.map((c) => (
              <button
                key={c.id}
                className={`contact ${peer?.id === c.id ? 'active' : ''}`}
                onClick={() => setPeer(c)}
              >
                <span className="avatar">{initials(c.nombre)}</span>
                <span className="contact-name">{c.nombre}</span>
              </button>
            ))}
          </div>
        </aside>

        <section className="msg-chat">
          {!peer ? (
              <div className="msg-empty">
                <div className="msg-empty-icon"><Icon name="chat" size={42} /></div>
                <p>Selecciona una persona de la lista para iniciar un chat privado.</p>
              </div>
          ) : (
            <>
              <div className="msg-header">
                <span className="avatar sm">{initials(peer.nombre)}</span>
                <div className="msg-header-info">
                  <strong>{peer.nombre}</strong>
                  <small>{peerOnline ? 'En línea' : 'Desconectado'}</small>
                </div>
                {!connected && <span className="msg-status">conectando…</span>}
              </div>

              <div className="msg-window">
                {messages.length === 0 && (
                  <div className="msg-start">Este es el inicio de tu conversación privada con {peer.nombre}.</div>
                )}
                {messages.map((m, i) => (
                  <div key={i} className={`msg-row ${m.mine ? 'mine' : ''}`}>
                    <div className="msg-bubble">
                      {m.content}
                      <span className="msg-time">{m.time}</span>
                    </div>
                  </div>
                ))}
                <div ref={endRef} />
              </div>

              <form onSubmit={send} className="msg-form">
                <EmojiPicker onSelect={(e) => setInput((prev) => prev + e)} />
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={`Escribe a ${peer.nombre}…`}
                />
                <button className="btn-primary" disabled={!connected}>Enviar</button>
              </form>
            </>
          )}
        </section>
      </div>
    </div>
  )
}
