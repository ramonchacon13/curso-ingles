import { useState, useEffect, useCallback } from "react"
import { useAuth } from "../context/AuthContext.jsx"
import { api } from "../api"

const NIVELES = ["A1", "A2", "B1", "B2", "C1", "C2"]
const ROLES = ["user", "moderator", "admin"]

export default function AdminUsuarios() {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [q, setQ] = useState("")
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState("")
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ nombre: "", email: "", role: "user", nivel: "A1", is_premium: false })
  const limit = 100

  const cargar = useCallback(async () => {
    setLoading(true)
    setMsg("")
    try {
      if (q.trim()) {
        const data = await api.get(`/admin/usuarios/buscar?q=${encodeURIComponent(q.trim())}`)
        setItems(data)
        setTotal(data.length)
      } else {
        const data = await api.get(`/admin/usuarios?page=${page}&limit=${limit}`)
        setItems(data.items || [])
        setTotal(data.total || 0)
      }
    } catch (e) {
      setMsg(e.message || "Error al cargar usuarios")
    } finally {
      setLoading(false)
    }
  }, [q, page])

  useEffect(() => { cargar() }, [cargar])

  function abrirEdicion(u) {
    setEditing(u)
    setForm({
      nombre: u.nombre,
      email: u.email,
      role: u.role || "user",
      nivel: u.nivel || "A1",
      is_premium: !!u.is_premium,
    })
    setMsg("")
  }

  async function guardarEdicion(e) {
    e.preventDefault()
    setMsg("")
    try {
      await api.put(`/admin/usuarios/${editing.id}`, form)
      setMsg("Usuario actualizado correctamente")
      setEditing(null)
      cargar()
    } catch (e) {
      setMsg(e.message || "Error al guardar")
    }
  }

  async function eliminar(u) {
    if (!window.confirm(
      `¿Eliminar la cuenta de "${u.nombre}" (${u.email})?\n\nSe borrará también su progreso, mensajes y resultados. Esta acción no se puede deshacer.`
    )) return
    setMsg("")
    try {
      await api.del(`/usuarios/${u.id}`)
      setMsg("Cuenta eliminada")
      cargar()
    } catch (e) {
      setMsg(e.message || "Error al eliminar")
    }
  }

  async function eliminarTodos() {
    if (!window.confirm(
      "¿Eliminar TODOS los usuarios excepto los administradores?\n\nSe borrará su progreso, mensajes y resultados. Esta acción no se puede deshacer."
    )) return
    setMsg("")
    try {
      const r = await api.del("/admin/usuarios")
      setMsg(`Se eliminaron ${r.eliminados} usuario(s) de prueba`)
      setPage(1)
      cargar()
    } catch (e) {
      setMsg(e.message || "Error al eliminar")
    }
  }

  if (!user || user.role !== "admin") {
    return (
      <div className="card">
        <p className="error">Acceso restringido a administradores</p>
      </div>
    )
  }

  const totalPag = Math.max(1, Math.ceil(total / limit))

  return (
    <div>
      <div className="card">
        <h2>Gestión de usuarios</h2>
        <p style={{ color: "#94a3b8", marginTop: "-4px" }}>
          Busca, edita o elimina cuentas para depurar la base de datos.
        </p>
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          <input
            placeholder="Buscar por nombre o correo"
            value={q}
            onChange={(e) => { setQ(e.target.value); setPage(1) }}
            style={{ flex: 1, minWidth: "220px" }}
          />
          {q && (
            <button className="btn-ghost" onClick={() => { setQ(""); setPage(1) }}>Limpiar</button>
          )}
          <button
            className="btn-ghost"
            style={{ color: "#ef4444", marginLeft: "auto" }}
            onClick={eliminarTodos}
          >Eliminar todos los de prueba</button>
        </div>
        {msg && (
          <p className={msg.includes("Error") ? "error" : "success"} style={{ marginTop: "8px" }}>{msg}</p>
        )}
      </div>

      <div className="card">
        {loading ? (
          <p>Cargando…</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Correo</th>
                <th>Rol</th>
                <th>Nivel</th>
                <th>Premium</th>
                <th>Registro</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ color: "#94a3b8" }}>No hay usuarios</td>
                </tr>
              ) : (
                items.map((u) => (
                  <tr key={u.id}>
                    <td>{u.nombre}</td>
                    <td>{u.email}</td>
                    <td>{u.role}</td>
                    <td>{u.nivel}</td>
                    <td>{u.is_premium ? "Sí" : "No"}</td>
                    <td>{u.created_at ? u.created_at.slice(0, 10) : "-"}</td>
                    <td>
                      <button className="btn-ghost" onClick={() => abrirEdicion(u)}>Editar</button>{" "}
                      <button
                        className="btn-ghost"
                        style={{ color: "#ef4444" }}
                        onClick={() => eliminar(u)}
                      >Eliminar</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}

        {!q && total > limit && (
          <div style={{ marginTop: "12px", display: "flex", gap: "8px", alignItems: "center" }}>
            <button className="btn-ghost" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>
              Anterior
            </button>
            <span>Página {page} de {totalPag}</span>
            <button className="btn-ghost" disabled={page >= totalPag} onClick={() => setPage((p) => p + 1)}>
              Siguiente
            </button>
          </div>
        )}
      </div>

      {editing && (
        <div
          onClick={() => setEditing(null)}
          style={{
            position: "fixed", inset: 0, background: "rgba(0,0,0,0.55)",
            display: "flex", alignItems: "center", justifyContent: "center", zIndex: 50, padding: "16px",
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#0f172a", border: "1px solid #1e293b", borderRadius: "12px",
              padding: "20px", width: "100%", maxWidth: "420px",
            }}
          >
            <h3 style={{ marginTop: 0 }}>Editar usuario #{editing.id}</h3>
            <form onSubmit={guardarEdicion}>
              <label style={{ display: "block", marginTop: "10px", fontSize: "13px", color: "#94a3b8" }}>Nombre</label>
              <input value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />

              <label style={{ display: "block", marginTop: "10px", fontSize: "13px", color: "#94a3b8" }}>Correo</label>
              <input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />

              <label style={{ display: "block", marginTop: "10px", fontSize: "13px", color: "#94a3b8" }}>Rol</label>
              <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>

              <label style={{ display: "block", marginTop: "10px", fontSize: "13px", color: "#94a3b8" }}>Nivel</label>
              <select value={form.nivel} onChange={(e) => setForm({ ...form, nivel: e.target.value })}>
                {NIVELES.map((n) => <option key={n} value={n}>{n}</option>)}
              </select>

              <label style={{ display: "flex", gap: "8px", alignItems: "center", marginTop: "12px" }}>
                <input
                  type="checkbox"
                  checked={form.is_premium}
                  onChange={(e) => setForm({ ...form, is_premium: e.target.checked })}
                />
                Usuario premium
              </label>

              {msg && msg.includes("Error") && <p className="error">{msg}</p>}

              <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end", marginTop: "16px" }}>
                <button type="button" className="btn-ghost" onClick={() => setEditing(null)}>Cancelar</button>
                <button type="submit" className="btn-primary">Guardar</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
