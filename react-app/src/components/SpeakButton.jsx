import { useEffect, useState } from 'react'
import Icon from './Icon.jsx'

let cachedVoice = null

function bestEnglishVoice() {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return null
  const vs = window.speechSynthesis.getVoices().filter(
    (v) => v.lang && v.lang.toLowerCase().startsWith('en')
  )
  if (!vs.length) return null
  const prefs = ['aria', 'neural', 'online', 'natural', 'samantha', 'google us english', 'zira', 'david', 'daniel']
  for (const p of prefs) {
    const found = vs.find((v) => v.name.toLowerCase().includes(p))
    if (found) return found
  }
  return vs[0]
}

export default function SpeakButton({ text, label = 'Escuchar pronunciación', size = 16 }) {
  const [speaking, setSpeaking] = useState(false)

  useEffect(() => {
    const load = () => {
      cachedVoice = bestEnglishVoice()
    }
    load()
    window.speechSynthesis.onvoiceschanged = load
    return () => {
      window.speechSynthesis.onvoiceschanged = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const onClick = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (!('speechSynthesis' in window) || !text) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'en-US'
    u.rate = 0.95
    const v = cachedVoice || bestEnglishVoice()
    if (v) u.voice = v
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
