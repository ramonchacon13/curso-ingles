const ES_ACCENT = /[áéíóúñü¿¡]/i
const ES_WORDS = [
  'perro', 'gato', 'pajaro', 'pájaro', 'presente', 'pasado', 'futuro',
  'rendirse', 'subir', 'dar', 'romper', 'refrescar', 'pintar', 'olvidar',
  'aunque', 'pero', 'porque', 'significa', 'verbo', 'sustantivo', 'adjetivo',
  'negativo', 'pregunta', 'ejemplo', 'traducción', 'nacionalidad', 'ella',
  'él', 'yo', 'tú', 'nosotros', 'ellos', 'está', 'muy', 'bien', 'casa',
  'libro', 'agua', 'comer', 'beber', 'dormir', 'hablar', 'pasiva',
  'comparativo', 'registro', 'conector', 'frase', 'lección', 'nivel',
  'ejercicio', 'respuesta',
]

export function isSpanish(text) {
  if (!text) return false
  const t = ' ' + text.toLowerCase() + ' '
  if (ES_ACCENT.test(t)) return true
  return ES_WORDS.some((w) => t.includes(' ' + w + ' '))
}
