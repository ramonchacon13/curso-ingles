const TOKEN_KEY = 'cursoingles_token'
const USER_KEY = 'cursoingles_user'
let memToken = null

export function getToken() {
  try {
    const t = localStorage.getItem(TOKEN_KEY)
    if (t) return t
  } catch {}
  return memToken
}

export function setSession(token, user) {
  memToken = token
  try {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  } catch {}
}

export function clearSession() {
  memToken = null
  try {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  } catch {}
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {}
  return null
}

export const API_BASE = import.meta.env.VITE_API_URL || 'https://curso-ingles-api.onrender.com'

async function request(method, path, body) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${API_BASE}/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (res.status === 401) {
    clearSession()
  }
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = new Error(data.detail || 'Error en la solicitud')
    err.status = res.status
    throw err
  }
  return data
}

export const api = {
  get: (p) => request('GET', p),
  post: (p, b) => request('POST', p, b),
  put: (p, b) => request('PUT', p, b),
  del: (p) => request('DELETE', p),
}

export const chatApi = {
  deleteMessage: (id) => api.del(`/chat/messages/${id}`),
}

export const aiApi = {
  tutor: (message, history = []) => api.post('/ai/tutor', { message, history }),
}

export const userApi = {
  progreso: () => api.get('/me/progreso'),
  updatePerfil: (data) => api.put('/me', data),
  updatePassword: (data) => api.put('/me/password', data),
  updateNivel: (nivel) => api.put('/me/nivel', { nivel }),
  completarLeccion: (id) => api.post(`/lecciones/${id}/completar`),
}
