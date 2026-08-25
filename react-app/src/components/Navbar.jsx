import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import Logo from './Logo.jsx'
import Icon from './Icon.jsx'
import Avatar from './Avatar.jsx'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
    setOpen(false)
  }

  const go = (to) => {
    navigate(to)
    setOpen(false)
  }

  return (
    <nav className="navbar">
      <Link to="/" className="brand" onClick={() => setOpen(false)}>
        <Logo size={30} />
        <span>Curso<b>Inglés</b></span>
      </Link>

      <button className="nav-toggle" onClick={() => setOpen(!open)} aria-label="Menú">
        <Icon name="menu" size={24} />
      </button>

      <div className={`nav-menu ${open ? 'open' : ''}`}>
        <div className="nav-links">
          <Link to="/cursos" onClick={() => setOpen(false)}>Cursos</Link>
          <Link to="/chat" onClick={() => setOpen(false)}>Chat</Link>
          <Link to="/mensajes" onClick={() => setOpen(false)}>Mensajes</Link>
          <Link to="/tests" onClick={() => setOpen(false)}>Tests</Link>
          <Link to="/practica-voz" onClick={() => setOpen(false)}>Practicar voz 🎙️</Link>
          <Link to="/perfil" onClick={() => setOpen(false)}>Perfil</Link>
          {user?.role === 'admin' && <Link to="/admin/usuarios" onClick={() => setOpen(false)}>Usuarios</Link>}
          {user?.is_premium && <Link to="/membresia" onClick={() => setOpen(false)}>Mi plan</Link>}
        </div>
        <div className="nav-user">
           {user ? (
              <>
                <Avatar user={user} size={32} />
                <span className="user-name">{user.nombre}</span>
                {user.role === 'admin' && <span className="role-badge admin">Admin</span>}
                {user.role === 'moderator' && <span className="role-badge moderator">Mod</span>}
                <button className="btn-ghost" onClick={handleLogout}>Salir</button>
              </>
           ) : (
            <>
              <Link to="/login" className="btn-ghost" onClick={() => setOpen(false)}>Entrar</Link>
              <Link to="/register" className="btn-primary" onClick={() => setOpen(false)}>Regístrate</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
