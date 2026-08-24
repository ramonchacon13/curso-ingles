import { useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
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
  const [searchParams, setSearchParams] = useSearchParams()
  const [recent, setRecent] = useState(() => {
    try { return JSON.parse(localStorage.getItem('pm_recent') || '[]') } catch { return [] }
  })
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [solicitudes, setSolicitudes] = useState([])
  const [peer, setPeer] = useState(null)
  const [accepted, setAccepted] = useState(false)
  const [pendingFromMe, setPendingFromMe] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [connected, setConnected] = useState(false)
  const [peerOnline, setPeerOnline] = useState(false)
  const wsRef = useRef(null)
  const endRef = useRef(null)
  const isAdmin = user?.role === 'admin'

  useEffect(() => {
    const pid = searchParams.get('peer')
    if (pid && !peer) {
      api.get(`/usuarios/${pid}`).then((r) => {
        const u = r.data
        setPeer({ id: u.id, nombre: u.nombre })
        addRecent({ id: u.id, nombre: u.nombre })
      }).catch(() => {})
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const addRecent = (c) => {
    setRecent((prev) => {
      const next = [c, ...prev.filter((x) => x.id !== c.id)].slice(0, 12)
      try { localStorage.setItem('pm_recent', JSON.stringify(next)) } catch {}
      return next
    })
  }

  useEffect(() => {
    if (!query.trim()) { setResults([]); return }
    const t = setTimeout(() => {
      api.get('/usuarios/buscar', { params: { q: query.trim() } })
        .then((r) => setResults(r.data))
        .catch(() => setResults([]))
    }, 300)
    return () => clearTimeout(t)
  }, [query])

  const loadSolicitudes = () =>
    api.get('/privado/solicitudes').then((r) => setSolicitudes(r.data)).catch(() => {})
  useEffect(() => {
    loadSolicitudes()
    const t = setInterval(loadSolicitudes, 10000)
    return () => clearInterval(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const selectPeer = async (c) => {
    setPeer(c)
    addRecent(c)
    setSearchParams({})
    setAccepted(false)
    try {
      await api.post('/privado/solicitar', { to_id: c.id })
      const st = await api.get('/privado/estado', { params: { peer_id: c.id } })
      if (st.data.status === 'accepted') setAccepted(true)
      else setPendingFromMe(!!st.data.from_me)
    } catch {}
  }

  useEffect(() => {
    if (!peer || accepted) return
    const t = setInterval(async () => {
      try {
        const r = await api.get('/privado/estado', { params: { peer_id: peer.id } })
        if (r.data.status === 'accepted') setAccepted(true)
      } catch {}
    }, 3000)
    return () => clearInterval(t)
  }, [peer, accepted])

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
        if (d.type === 'status') { setAccepted(!!d.accepted); return }
        if (d.type === 'accepted') { setAccepted(true); return }
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
    if (!t || !wsRef.current || wsRef.current.readyState !== 1 || !accepted) return
    wsRef.current.send(t)
    setInput('')
  }

  const aceptar = async (s) => {
    try {
      await api.post(`/privado/solicitudes/${s.id}/aceptar`)
      setSolicitudes((sols) => sols.filter((x) => x.id !== s.id))
      setPeer({ id: s.from_id, nombre: s.from_nombre })
    } catch {}
  }
  const rechazar = async (s) => {
    try {
      await api.post(`/privado/solicitudes/${s.id}/rechazar`)
      setSolicitudes((sols) => sols.filter((x) => x.id !== s.id))
    } catch {}
  }

  const deleteUser = async () => {
    if (!peer) return
    if (!window.confirm(`¿Eliminar a ${peer.nombre} y todos sus datos de forma permanente?`)) return
    try {
      await api.delete(`/usuarios/${peer.id}`)
      const next = recent.filter((x) => x.id !== peer.id)
      setRecent(next)
      try { localStorage.setItem('pm_recent', JSON.stringify(next)) } catch {}
      setPeer(null)
    } catch (e) {
      window.alert(e?.response?.data?.detail || 'No se pudo eliminar el usuario')
    }
  }

  return (
    <div className="mensajes">
      <h1 className="mensajes-title">
        Mensajes privados
        {solicitudes.length > 0 && <span className="sol-badge">{solicitudes.length}</span>}
      </h1>
      <div className="msg-layout">
        <aside className="msg-sidebar">
          <div className="msg-sidebar-head">Conversar</div>

          {solicitudes.length > 0 && (
            <div className="sol-box">
              <div className="sol-title">Solicitudes recibidas</div>
              {solicitudes.map((s) => (
                <div key={s.id} className="sol-item">
                  <span className="sol-name">{s.from_nombre}</span>
                  <div className="sol-actions">
                    <button className="btn-ghost sol-ok" onClick={() => aceptar(s)}>Aceptar</button>
                    <button className="btn-ghost sol-no" onClick={() => rechazar(s)}>Rechazar</button>
                  </div>
                </div>
              ))}
            </div>
          )}

          <input
            className="msg-search"
            placeholder="Buscar usuario por nombre o correo…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <div className="msg-contacts">
            {query.trim() ? (
              results.length === 0 ? (
                <p className="muted" style={{ padding: '12px' }}>Sin coincidencias.</p>
              ) : (
                results.map((c) => (
                  <button key={c.id} className="contact" onClick={() => selectPeer(c)}>
                    <span className="avatar">{initials(c.nombre)}</span>
                    <span className="contact-name">{c.nombre}</span>
                  </button>
                ))
              )
            ) : recent.length === 0 ? (
              <p className="muted" style={{ padding: '12px' }}>Busca un usuario para iniciar un chat privado.</p>
            ) : (
              recent.map((c) => (
                <button
                  key={c.id}
                  className={`contact ${peer?.id === c.id ? 'active' : ''}`}
                  onClick={() => selectPeer(c)}
                >
                  <span className="avatar">{initials(c.nombre)}</span>
                  <span className="contact-name">{c.nombre}</span>
                </button>
              ))
            )}
          </div>
        </aside>

        <section className="msg-chat">
          {!peer ? (
            <div className="msg-empty">
              <div className="msg-empty-icon"><Icon name="chat" size={42} /></div>
              <p>Busca un usuario en la barra lateral para enviarle una solicitud de chat privado.</p>
            </div>
          ) : (
            <>
              <div className="msg-header">
                <span className="avatar sm">{initials(peer.nombre)}</span>
                <div className="msg-header-info">
                  <strong>{peer.nombre}</strong>
                  <small>{peerOnline ? 'En línea' : 'Desconectado'}</small>
                </div>
                {isAdmin && peer.id !== user.id && (
                  <button className="msg-del-user" title="Eliminar usuario" onClick={deleteUser}>
                    <Icon name="trash" size={16} />
                  </button>
                )}
                {!connected && <span className="msg-status">conectando…</span>}
              </div>

              {!accepted && (
                <div className="msg-pending">
                  {pendingFromMe
                    ? `Esperando que ${peer.nombre} acepte tu solicitud de chat privado…`
                    : `${peer.nombre} te envió una solicitud de chat. Acéptala para conversar.`}
                </div>
              )}

              <div className="msg-window">
                {messages.length === 0 && accepted && (
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
                  placeholder={accepted ? `Escribe a ${peer.nombre}…` : 'Esperando aceptación…'}
                  disabled={!accepted}
                />
                <button className="btn-primary" disabled={!connected || !accepted}>Enviar</button>
              </form>
            </>
          )}
        </section>
      </div>
    </div>
  )
}
