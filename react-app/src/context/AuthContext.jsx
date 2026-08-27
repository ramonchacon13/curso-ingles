import { createContext, useContext, useState } from 'react'
import { api, getStoredUser, setSession, clearSession } from '../api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser())


  const login = async (email, password) => {
    const data = await api.post('/auth/login', { email, password })
    setSession(data.token, data.user)
    setUser(data.user)
    return data.user
  }

  const register = async (nombre, email, password) => {
    const data = await api.post('/auth/register', { nombre, email, password })
    return data
  }

  const logout = () => {
    clearSession()
    setUser(null)
  }

  const refresh = async () => {
    try {
      const u = await api.get('/auth/me')
      setUser(u)
      return u
    } catch {
      return null
    }
  }

  return (
    <AuthContext.Provider value={{ user, setUser, login, register, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
