import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { api } from '../api.js'
import { DONACION } from '../config.js'
import Icon from '../components/Icon.jsx'

export default function Membership() {
  const { user, refresh } = useAuth()
  const [info, setInfo] = useState(null)
  const [msg, setMsg] = useState('')
  const [copiado, setCopiado] = useState(false)

  const load = () => {
    api.get('/membresia').then(setInfo).catch(() => {})
  }
  useEffect(load, [])

  const activate = async () => {
    setMsg('')
    try {
      await api.post('/membresia/activar')
      await refresh()
      setMsg('¡Membresía premium activada! (demo)')
      load()
    } catch (e) {
      setMsg(e.message)
    }
  }

  const cancel = async () => {
    setMsg('')
    try {
      await api.post('/membresia/cancelar')
      await refresh()
      setMsg('Membresía cancelada.')
      load()
    } catch (e) {
      setMsg(e.message)
    }
  }

  const copiar = async () => {
    try {
      await navigator.clipboard.writeText(DONACION.binancePayId)
      setCopiado(true)
      setTimeout(() => setCopiado(false), 2000)
    } catch {
      setCopiado(false)
    }
  }

  return (
    <div className="membership">
      <h1>Membresía</h1>
      {msg && <div className="alert-ok">{msg}</div>}
      <div className="plan-card">
        <h2>Plan actual: <strong>{user?.plan === 'premium' ? 'Premium' : 'Gratis'}</strong></h2>
        <p>{info ? `Desde $${info.precio_mensual} / mes` : ''}</p>

        {user?.is_premium ? (
          <>
            <p className="ok-text">Disfrutas de todas las lecciones premium y el material exclusivo.</p>
            <button className="btn-secondary" onClick={cancel}>Cancelar membresía</button>
          </>
        ) : (
          <>
            <h3>Beneficios premium</h3>
            <ul className="benefits">
              <li>✔ Todas las lecciones premium</li>
              <li>✔ Material descargable y ejercicios extra</li>
              <li>✔ Soporte prioritario en el chat de la comunidad</li>
            </ul>
            <button className="btn-primary" onClick={activate}>Activar premium (demo)</button>
          </>
        )}
      </div>

      <div className="donate-card">
        <h2><Icon name="star" size={20} /> Apoya Best English</h2>
        <p>Tu aporte nos ayuda a mantener la plataforma y crear más contenido gratis.</p>

        <a className="pay-btn paypal" href={DONACION.paypal} target="_blank" rel="noopener noreferrer">
          Donar con PayPal
        </a>

        <div className="pay-binance">
          <div>
            <span className="pay-label">Binance Pay ID</span>
            <strong className="pay-id">{DONACION.binancePayId}</strong>
          </div>
          <button className="btn-ghost" onClick={copiar}>{copiado ? '¡Copiado!' : 'Copiar'}</button>
        </div>
        <p className="muted">Envía tu aporte por Binance Pay a ese ID desde la app de Binance.</p>

        <p className="donate-note">{DONACION.nota}</p>
      </div>
    </div>
  )
}
