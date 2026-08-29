import { useState } from 'react'
import { CATEGORIES, STORY } from '../data/frases.js'
import SpeakButton from '../components/SpeakButton.jsx'

const KNOWN_KEY = 'bestenglish_frases_known'

function hash(str) {
  let h = 0
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0
  return h
}

function imgUrl(tag, seed) {
  return `https://loremflickr.com/480/320/${tag}?lock=${(hash(seed) % 1000) + 1}`
}

function loadKnown() {
  try {
    return JSON.parse(localStorage.getItem(KNOWN_KEY) || '{}')
  } catch {
    return {}
  }
}

export default function Frases() {
  const [tab, setTab] = useState('temas')
  const [catId, setCatId] = useState(CATEGORIES[0].id)
  const [revealed, setRevealed] = useState({})
  const [known, setKnown] = useState(loadKnown())
  const [storyRevealed, setStoryRevealed] = useState({})

  const cat = CATEGORIES.find((c) => c.id === catId)

  const toggleReveal = (id) => setRevealed((r) => ({ ...r, [id]: !r[id] }))
  const markKnown = (id) => {
    const next = { ...known, [id]: !known[id] }
    setKnown(next)
    try {
      localStorage.setItem(KNOWN_KEY, JSON.stringify(next))
    } catch {}
  }
  const knownCount = Object.values(known).filter(Boolean).length

  return (
    <div className="frases-page">
      <h1>Frases de la vida real 💬</h1>
      <p className="muted">
        Toca el altavoz para escuchar la pronunciación. Revela la traducción y marca las frases que ya dominas.
      </p>

      <div className="mode-tabs">
        <button className={tab === 'temas' ? 'on' : ''} onClick={() => setTab('temas')}>Por tema</button>
        <button className={tab === 'historia' ? 'on' : ''} onClick={() => setTab('historia')}>Historia interactiva</button>
      </div>

      {tab === 'temas' && (
        <>
          <div className="cat-tabs">
            {CATEGORIES.map((c) => (
              <button
                key={c.id}
                className={catId === c.id ? 'on' : ''}
                onClick={() => setCatId(c.id)}
              >
                {c.title}
              </button>
            ))}
          </div>

          <p className="muted small">Dominadas en este tema: {cat.phrases.filter((_, i) => known[`${cat.id}-${i}`]).length} / {cat.phrases.length} · total {knownCount}</p>

          <div className="phrase-list">
            {cat.phrases.map((p, i) => {
              const id = `${cat.id}-${i}`
              return (
                <div key={id} className={`phrase-card ${known[id] ? 'known' : ''}`}>
                  <img className="phrase-img" src={imgUrl(cat.img, cat.id)} alt={cat.title} loading="lazy" />
                  <div className="phrase-en">
                    <SpeakButton text={p.en} />
                    <span>{p.en}</span>
                  </div>
                  {revealed[id] && <div className="phrase-es">{p.es}</div>}
                  <div className="phrase-actions">
                    <button className="btn-ghost" onClick={() => toggleReveal(id)}>
                      {revealed[id] ? 'Ocultar traducción' : 'Ver traducción'}
                    </button>
                    <button
                      className={`btn-ghost ${known[id] ? 'on' : ''}`}
                      onClick={() => markKnown(id)}
                    >
                      {known[id] ? '✓ Lo sé' : 'Marcar lo sé'}
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        </>
      )}

      {tab === 'historia' && (
        <div className="story">
          <h2>{STORY.title}</h2>
          <p className="muted small">Lee la historia y escucha cada línea. Toca para ver la traducción.</p>
          {STORY.lines.map((l, i) => {
            const id = `s-${i}`
            return (
              <div key={id} className="story-line">
                <img className="story-img" src={imgUrl(l.img, `story-${i}`)} alt={l.speaker} loading="lazy" />
                <div className="story-speaker">{l.speaker}</div>
                <div className="story-en">
                  <SpeakButton text={l.en} />
                  <span>{l.en}</span>
                </div>
                {storyRevealed[id] && <div className="story-es">{l.es}</div>}
                <button className="btn-ghost" onClick={() => setStoryRevealed((s) => ({ ...s, [id]: !s[id] }))}>
                  {storyRevealed[id] ? 'Ocultar traducción' : 'Ver traducción'}
                </button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
