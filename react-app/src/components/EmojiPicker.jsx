import { useState } from 'react'
import Icon from './Icon.jsx'

const EMOJIS = [
  '😀', '😂', '😍', '😎', '🤔', '😅', '😉', '😢', '😭', '🥳',
  '👍', '👎', '🙏', '💪', '🤝', '❤️', '🔥', '🎉', '⭐', '🌟',
  '💯', '✅', '📚', '💬', '🚀', '⏰', '👋', '🙌', '😴', '🍕',
]

export default function EmojiPicker({ onSelect }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="emoji-wrap">
      <button
        type="button"
        className="emoji-btn"
        onClick={() => setOpen(!open)}
        aria-label="Emojis"
        title="Emojis"
      >
        <Icon name="smile" size={22} />
      </button>
      {open && (
        <div className="emoji-pop">
          {EMOJIS.map((e) => (
            <button
              type="button"
              key={e}
              className="emoji-item"
              onClick={() => { onSelect(e); setOpen(false) }}
            >
              {e}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
