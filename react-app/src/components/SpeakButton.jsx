import { useState } from 'react'
import Icon from './Icon.jsx'

export default function SpeakButton({ text, label = 'Escuchar pronunciación', size = 16 }) {
  const [speaking, setSpeaking] = useState(false)

  const onClick = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (!('speechSynthesis' in window) || !text) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'en-US'
    u.rate = 0.95
    u.onstart = () => setSpeaking(true)
    u.onend = () => setSpeaking(false)
    u.onerror = () => setSpeaking(false)
    window.speechSynthesis.speak(u)
  }

  return (
    <button
      type="button"
      className={`speak-btn ${speaking ? 'speaking' : ''}`}
      onClick={onClick}
      title={label}
      aria-label={label}
    >
      <Icon name="volume" size={size} />
    </button>
  )
}
