import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { userApi } from '../api.js'
import Icon from '../components/Icon.jsx'
import Avatar from '../components/Avatar.jsx'

const NIVELES = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

export default function Perfil() {
  const { user, setUser, refresh } = useAuth()
  const [nombre, setNombre] = useState(user?.nombre || '')
  const [nivel, setNivel] = useState(user?.nivel || 'A1')
  const [actual, setActual] = useState('')
  const [nueva, setNueva] = useState('')
  const [repetir, setRepetir] = useState('')
  const [progreso, setProgreso] = useState(null)
  const [optIn, setOptIn] = useState(user?.email_opt_in ?? true)
  const [avatarKind, setAvatarKind] = useState(user?.avatar_kind || 'initials')
  const [avatarValue, setAvatarValue] = useState(user?.avatar_value || '')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  useEffect(() => {
    userApi.progreso().then(setProgreso).catch(() => {})
  }, [])

  const guardarPerfil = async (e) => {
    e.preventDefault()
    setMsg(''); setErr('')
    try {
      await userApi.updatePerfil({ nombre, email_opt_in: optIn, avatar_kind: avatarKind, avatar_value: avatarValue || null })
      await refresh()
      setMsg('Perfil actualizado.')
    } catch (e2) {
      setErr(e2.message)
    }
  }

  const guardarNivel = async (e) => {
    e.preventDefault()
    setMsg(''); setErr('')
    try {
      await userApi.updateNivel(nivel)
      await refresh()
      setMsg('Nivel actualizado.')
    } catch (e2) {
      setErr(e2.message)
    }
  }

  const cambiarPassword = async (e) => {
    e.preventDefault()
    setMsg(''); setErr('')
    if (nueva !== repetir) { setErr('Las contraseñas no coinciden.'); return }
    if (nueva.length < 4) { setErr('La contraseña es muy corta.'); return }
    try {
      await userApi.updatePassword({ actual, nueva })
      setActual(''); setNueva(''); setRepetir('')
      setMsg('Contraseña actualizada.')
    } catch (e2) {
      setErr(e2.message)
    }
  }

  const EMOJIS = ['🦊', '🐱', '🐶', '🦁', '🐼', '🐨', '🐸', '🐵', '🦄', '🐯', '🐰', '🐻', '🐧', '🦉', '🌟', '🔥', '🌈', '⚡', '🍀', '🌸', '👽', '🤖', '💡', '🎯']

  const pickEmoji = (e) => {
    setAvatarKind('emoji')
    setAvatarValue(e)
  }

  const onFile = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const img = new Image()
      img.onload = () => {
        const max = 160
        const scale = Math.min(1, max / Math.max(img.width, img.height))
        const w = Math.max(1, Math.round(img.width * scale))
        const h = Math.max(1, Math.round(img.height * scale))
        const canvas = document.createElement('canvas')
        canvas.width = w
        canvas.height = h
        canvas.getContext('2d').drawImage(img, 0, 0, w, h)
        setAvatarValue(canvas.toDataURL('image/png'))
        setAvatarKind('image')
      }
      img.src = reader.result
    }
    reader.readAsDataURL(file)
  }

  return (
    <div className="page narrow">
      <h1><Icon name="user" size={26} /> Mi perfil</h1>
      {msg && <div className="alert ok">{msg}</div>}
      {err && <div className="alert error">{err}</div>}

      <section className="card">
        <h2>Avatar</h2>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <Avatar user={{ id: user?.id, nombre: nombre || user?.nombre, avatar_kind: avatarKind, avatar_value: avatarValue || null }} size={80} />
          <div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <button type="button" className={avatarKind === 'initials' ? 'btn-primary' : 'btn-ghost'} onClick={() => { setAvatarKind('initials'); setAvatarValue('') }}>Iniciales</button>
              <button type="button" className={avatarKind === 'emoji' ? 'btn-primary' : 'btn-ghost'} onClick={() => { setAvatarKind('emoji'); if (!avatarValue) setAvatarValue(EMOJIS[0]) }}>Emoji</button>
              <label className="btn-ghost" style={{ cursor: 'pointer' }}>
                Imagen
                <input type="file" accept="image/*" onChange={onFile} style={{ display: 'none' }} />
              </label>
            </div>
            {avatarKind === 'emoji' && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: '4px', marginTop: '10px', maxWidth: '340px' }}>
                {EMOJIS.map((e) => (
                  <button key={e} type="button" onClick={() => pickEmoji(e)} style={{ fontSize: '22px', padding: '4px', border: avatarValue === e ? '2px solid #6366f1' : '1px solid #334155', borderRadius: '8px', background: '#0f172a' }}>{e}</button>
                ))}
              </div>
            )}
            {avatarKind === 'image' && avatarValue && (
              <p className="muted" style={{ marginTop: '8px' }}>Imagen lista. Guarda para aplicar.</p>
            )}
          </div>
        </div>
      </section>

      <section className="card">
        <h2>Datos personales</h2>
        <form onSubmit={guardarPerfil} className="form-col">
          <label>Nombre
            <input value={nombre} onChange={(e) => setNombre(e.target.value)} />
          </label>
          <label>Correo
            <input value={user?.email} disabled />
          </label>
          <button className="btn-primary" type="submit">Guardar nombre</button>
        </form>
      </section>

      <section className="card">
        <h2>Correos</h2>
        <p className="muted">Te enviaremos solo lo importante. Marca esta opción para recibir un resumen semanal de tu progreso.</p>
        <label className="checkbox-row">
          <input type="checkbox" checked={optIn} onChange={(e) => setOptIn(e.target.checked)} />
          Quiero recibir un resumen semanal por correo
        </label>
      </section>

      <section className="card">
        <h2>Mi nivel</h2>
        <p className="muted">Tu nivel actual también se actualiza automáticamente al aprobar un test.</p>
        <form onSubmit={guardarNivel} className="form-row">
          <select value={nivel} onChange={(e) => setNivel(e.target.value)}>
            {NIVELES.map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
          <button className="btn-primary" type="submit">Cambiar nivel</button>
        </form>
      </section>

      <section className="card">
        <h2>Cambiar contraseña</h2>
        <form onSubmit={cambiarPassword} className="form-col">
          <label>Contraseña actual
            <input type="password" value={actual} onChange={(e) => setActual(e.target.value)} />
          </label>
          <label>Nueva contraseña
            <input type="password" value={nueva} onChange={(e) => setNueva(e.target.value)} />
          </label>
          <label>Repetir nueva contraseña
            <input type="password" value={repetir} onChange={(e) => setRepetir(e.target.value)} />
          </label>
          <button className="btn-primary" type="submit">Actualizar contraseña</button>
        </form>
      </section>

      <section className="card">
        <h2>Mi progreso</h2>
        {progreso && (
          <>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progreso.porcentaje}%` }} />
            </div>
            <p className="muted">{progreso.completadas} de {progreso.total_lecciones} lecciones completadas ({progreso.porcentaje}%)</p>
            <div className="progress-levels">
              {Object.entries(progreso.by_level).map(([code, info]) => (
                <div key={code} className="progress-level">
                  <span className="pl-code">{code}</span>
                  <span className="pl-count">{info.completadas}/{info.total}</span>
                  <div className="progress-bar small">
                    <div className="progress-fill" style={{ width: `${info.total ? (info.completadas / info.total * 100) : 0}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  )
}
