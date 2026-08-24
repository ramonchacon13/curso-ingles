const TOKEN_KEY = 'cursoingles_token'
const USER_KEY = 'cursoingles_user'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY)
  return raw ? JSON.parse(raw) : null
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
    throw new Error(data.detail || 'Error en la solicitud')
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
