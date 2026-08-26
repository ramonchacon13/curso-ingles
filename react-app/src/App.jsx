import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext.jsx'
import Navbar from './components/Navbar.jsx'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import OAuthCallback from './pages/OAuthCallback.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Courses from './pages/Courses.jsx'
import Lesson from './pages/Lesson.jsx'
import Chat from './pages/Chat.jsx'
import Tests from './pages/Tests.jsx'
import Membership from './pages/Membership.jsx'
import PracticaVoz from './pages/PracticaVoz.jsx'
import Mensajes from './pages/Mensajes.jsx'
import Perfil from './pages/Perfil.jsx'
import AdminUsuarios from './pages/AdminUsuarios.jsx'

function Private({ children }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  const { user } = useAuth()
  return (
    <div className="app">
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
          <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <Register />} />
          <Route path="/oauth-callback" element={<OAuthCallback />} />
          <Route path="/dashboard" element={<Private><Dashboard /></Private>} />
          <Route path="/cursos" element={<Private><Courses /></Private>} />
          <Route path="/lecciones/:id" element={<Private><Lesson /></Private>} />
          <Route path="/chat" element={<Private><Chat /></Private>} />
          <Route path="/mensajes" element={<Private><Mensajes /></Private>} />
          <Route path="/tests" element={<Private><Tests /></Private>} />
          <Route path="/practica-voz" element={<PracticaVoz />} />
          <Route path="/membresia" element={<Private><Membership /></Private>} />
          <Route path="/perfil" element={<Private><Perfil /></Private>} />
          <Route path="/admin/usuarios" element={<Private><AdminUsuarios /></Private>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
      <footer className="footer">
        <p>© {new Date().getFullYear()} Best English · Aprende inglés gratis</p>
      </footer>
    </div>
  )
}
