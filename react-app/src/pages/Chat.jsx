import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { getToken } from '../api.js'
import Icon from '../components/Icon.jsx'
import EmojiPicker from '../components/EmojiPicker.jsx'

function nowTime() {
  return new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

export default function Chat() {
  const { user } = useAuth()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [online, setOnline] = useState(0)
  const [connected, setConnected] = useState(false)
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
        } else if (data.type === 'msg') {
          setMessages((m) => [...m, {
            user: data.user,
            content: data.content,
            time: data.time ? data.time.slice(11, 16) : nowTime(),
            mine: data.user === user?.nombre,
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

  return (
    <div className="chat-page">
      <h1><Icon name="chat" size={26} /> Chat de la comunidad</h1>
      <p className="chat-sub">
        <span className={`status-dot ${connected ? 'on' : 'off'}`} />
        {connected ? 'En línea' : 'Conectando...'} ·
        {' '}{online} usuario(s) en el chat
      </p>
      <div className="chat-window">
        {messages.length === 0 && <div className="chat-empty">Sé el primero en saludar en el chat.</div>}
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.mine ? 'user' : 'assistant'}`}>
            <div className="bubble-head"><strong>{m.user}</strong> <span className="bubble-time">{m.time}</span></div>
            {m.content}
          </div>
        ))}
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
