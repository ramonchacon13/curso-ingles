const ES_ACCENT = /[áéíóúñü¿¡]/i
const ES_SUFFIX = /(ción|sión|mente|ista|aje|oso|osa|ico|ica|able|ible|ador|adora|ero|era|ito|ita|udo|uda|án|én|ín|ón)$/i

// Palabras/marcadores en español (se compara con espacios alrededor para no dar falsos positivos)
const ES_WORDS = [
  'cómo', 'como', 'se', 'dice', 'yo', 'soy', 'eres', 'es', 'son', 'está', 'estan', 'fue', 'fui',
  'pronombre', 'para', 'ella', 'él', 'el', 'la', 'los', 'las', 'una', 'un', 'unos', 'unas',
  'gato', 'pájaro', 'gracias', 'inglés', 'libro', 'mesa', 'coche', 'forma', 'negativa', 'negativo',
  'buenos', 'días', 'refiere', 'cuál', 'plural', 'tengo', 'perro', 'fuego', 'agua', 'viento',
  'articulo', 'artículo', 'usas', 'usa', 'antes', 'vocal', 'preguntas', 'te', 'llamas', 'sí', 'quizás',
  'adjetivo', 'verbo', 'amigo', 'familia', 'profesor', 'entiendo', 'pasado', 'futuro', 'semana',
  'meses', 'años', 'hiciste', 'feliz', 'largo', 'caro', 'barato', 'obligación', 'fuerte', 'posibilidad',
  'prohibición', 'presente', 'perfecto', 'introduce', 'acción', 'progreso', 'decisión', 'sin', 'embargo',
  'también', 'suger', 'compra', 'comido', 'tarea', 'debe', 'punto', 'tiempo', 'doctor', 'mate', 'médico',
  'pequeño', 'comparativo', 'superlativo', 'solía', 'jugar', 'aunque', 'pero', 'persona', 'estudio',
  'desde', 'trabajo', 'proyecto', 'leche', 'todavía', 'aún', 'esta', 'noche', 'casa', 'comer', 'beber',
  'dormir', 'hablar', 'libro', 'agua', 'muy', 'bien', 'mal', 'aquí', 'allí', 'este', 'esta', 'ese',
  'esa', 'aquel', 'traduce', 'sirve', 'indica', 'significa', 'estilo', 'indirecto', 'expresiones',
  'idiomáticas', 'académico', 'matrices', 'matiz', 'registro', 'conector', 'argumentación', 'modales',
  'probabilidad', 'debate', 'cláusula', 'reported', 'phrasal', 'relativo', 'posesión', 'sujeto',
  'objeto', 'inherente', 'heredado', 'interno', 'subrayar', 'restar', 'bajar', 'prominente', 'salado',
  'interpolar', 'extrapolar', 'extraer', 'incuestionable', 'controvertido', 'cuestionable', 'arquetípico',
  'evitar', 'abrazar', 'esconder', 'secundario', 'clave', 'pasivo', 'borrar', 'delinear', 'retirar',
  'confundir', 'oscurecer', 'obstruir', 'diluir', 'dibujar', 'discernir', 'señalar', 'manifestar',
  'cotejar', 'conjeturar', 'disentir', 'refutar', 'rehusar', 'agravar', 'mitigar', 'prever', 'nominal',
  'incluir', 'excluir', 'correr', 'desconocido', 'discrepar', 'coincidir', 'saliente', 'por', 'porque',
  'cuando', 'donde', 'qué', 'y', 'o', 'de', 'del', 'al', 'con', 'sin', 'pero', 'a', 'en', 'lo', 'le',
  'les', 'mi', 'tu', 'su', 'me', 'nos', 'se', 'hay', 'esto', 'esa', 'aquel', 'tanto', 'modo', 'efecto',
  'práctica', 'medida', 'ignorar', 'aunque', 'tres', 'uno', 'dos', 'bueno', 'malo', 'ejemplar', 'grande',
  'notable', 'técnico', 'frase', 'adjetivo', 'conceder', 'negar', 'preguntar', 'intencional', 'propósito',
  'indudable', 'legal', 'especial', 'menos', 'suponer', 'posar', 'supuesta', 'intencionalmente',
  'prácticamente', 'legalmente', 'indudablemente', 'supuestamente', 'especialmente', 'nada', 'mismo',
  'puede', 'ver', 'pasar', 'pesar', 'a', 'del', 'mismo', 'excelente', 'neutro', 'positivo', 'coloquial',
  'vulgo', 'formal', 'frecuencia', 'adelantar', 'común', 'posesión', 'oposición', 'resultado', 'adición',
  'causa', 'persuadir', 'saludar', 'despedir', 'del', 'manera', 'a', 'pesar', 'pese', 'a',
]

// Núcleo de palabras en inglés (para no ocultar audio en palabras sueltas en inglés)
const EN_CORE = [
  'i', 'am', 'is', 'are', 'was', 'were', 'he', 'she', 'it', 'they', 'we', 'you', 'go', 'went', 'gone',
  'eat', 'ate', 'eaten', 'like', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'can',
  'could', 'must', 'may', 'might', 'shall', 'should', 'this', 'that', 'what', 'when', 'where', 'how',
  'who', 'whom', 'whose', 'the', 'a', 'an', 'my', 'your', 'his', 'her', 'our', 'their', 'me', 'him',
  'us', 'them', 'to', 'of', 'in', 'on', 'for', 'with', 'at', 'by', 'from', 'yes', 'no', 'hello', 'hi',
  'thanks', 'please', 'sorry', 'good', 'bad', 'big', 'small', 'happy', 'long', 'red', 'blue', 'water',
  'book', 'cat', 'dog', 'apple', 'friend', 'home', 'time', 'day', 'year', 'love', 'hate', 'study',
  'play', 'watch', 'help', 'see', 'know', 'think', 'want', 'need', 'make', 'take', 'come', 'give',
  'find', 'tell', 'ask', 'work', 'live', 'learn', 'read', 'write', 'speak', 'listen', 'drink', 'sleep',
  'thank', 'morning', 'night', 'goodbye', 'name', 'student', 'teacher', 'doctor', 'then', 'more', 'most',
  'than', 'cats', 'tree', 'table', 'park', 'week', 'month', 'tv', 'near', 'far', 'next', 'football',
  'hair', 'math', 'milk', 'homework', 'already', 'yet', 'still', 'tonight', 'leave', 'buy', 'bought',
  'state', 'leave', 'interested', 'music', 'although', 'third', 'person', 'since', 'run', 'negative',
  'furthermore', 'nevertheless', 'albeit', 'substantial', 'huge', 'large', 'considerable', 'exemplary',
  'inherent', 'pivotal', 'salient', 'quintessential', 'allegedly', 'eschew', 'loathe', 'gainsay',
  'obfuscate', 'extrapolate', 'incontrovertible', 'delineate', 'underscore', 'mitigate', 'preclude',
  'concur', 'posit', 'brook', 'aforementioned', 'notwithstanding', 'thereby', 'arguably', 'admittedly',
  'insofar', 'former', 'latter', 'per', 'same', 'token', 'extent', 'formal', 'colloquial', 'academic',
  'neutr', 'positive', 'negative', 'result', 'opposition', 'addition', 'cause', 'persuade', 'greet',
  'farewell', 'ignore', 'because', 'although', 'but', 'and', 'or', 'not', 'into', 'about', 'over',
  'under', 'behind', 'above', 'below', 'between', 'during', 'before', 'after', 'always', 'never',
  'often', 'sometimes', 'usually', 'break', 'ice', 'brush', 'look', 'turn', 'put', 'take', 'get',
  'set', 'come', 'rule', 'ward', 'fall', 'stand', 'carry', 'make', 'bring', 'account', 'piece', 'cake',
  'moon', 'hardly', 'rarely', 'scarcely', 'only', 'little', 'few', 'much', 'many', 'both', 'any',
  'some', 'every', 'each', 'other', 'another', 'such', 'own', 'same', 'different', 'real', 'true',
]

export function isSpanish(text) {
  if (!text || typeof text !== 'string') return false
  if (ES_ACCENT.test(text)) return true
  if (ES_SUFFIX.test(text.trim())) return true
  const t = ' ' + text.toLowerCase() + ' '
  if (ES_WORDS.some((w) => t.includes(' ' + w + ' '))) return true
  const tokens = text.trim().split(/\s+/)
  if (tokens.length === 1) {
    const w = tokens[0].replace(/[^a-z]/gi, '').toLowerCase()
    if (w && !EN_CORE.includes(w)) return true
  }
  return false
}
