from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from database import get_db
from models import User, Progreso, Lesson, Level, Course, PrivateMessage, ChatMessage, TestResult, SolicitudPrivada
from auth_deps import get_current_user
from auth_utils import hash_password, verify_password
from sqlalchemy import select, func, delete

router = APIRouter(prefix="/api", tags=["usuarios"])

NIVELES_VALIDOS = ["A1", "A2", "B1", "B2", "C1", "C2"]


class NivelUpdate(BaseModel):
    nivel: str


class PerfilUpdate(BaseModel):
    nombre: str | None = None
    email: str | None = None
    email_opt_in: bool | None = None


class PasswordUpdate(BaseModel):
    actual: str
    nueva: str


@router.put("/me", response_model=dict)
def update_perfil(
    data: PerfilUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if data.nombre is not None and data.nombre.strip():
        current.nombre = data.nombre.strip()
    if data.email is not None and data.email.strip():
        nuevo = data.email.strip().lower()
        if nuevo != current.email:
            existe = db.scalar(select(User).where(User.email == nuevo, User.id != current.id))
            if existe:
                raise HTTPException(status_code=400, detail="El correo ya está registrado")
            current.email = nuevo
    if data.email_opt_in is not None:
        current.email_opt_in = bool(data.email_opt_in)
    db.commit()
    return {"ok": True, "nombre": current.nombre, "email": current.email, "email_opt_in": current.email_opt_in}


@router.put("/me/password", response_model=dict)
def update_password(
    data: PasswordUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not verify_password(data.actual, current.hashed_password):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")
    if len(data.nueva) < 4:
        raise HTTPException(status_code=400, detail="La nueva contraseña es muy corta")
    current.hashed_password = hash_password(data.nueva)
    db.commit()
    return {"ok": True}


@router.put("/me/nivel", response_model=dict)
def update_nivel(
    data: NivelUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if data.nivel not in NIVELES_VALIDOS:
        return {"ok": False, "detail": "Nivel inválido"}
    current.nivel = data.nivel
    db.commit()
    return {"ok": True, "nivel": current.nivel}


@router.get("/me/progreso", response_model=dict)
def mi_progreso(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    completadas = db.scalars(
        select(Progreso.lesson_id).where(Progreso.user_id == current.id)
    ).all()
    total_lecciones = db.scalar(select(func.count(Lesson.id))) or 0
    total_niveles = db.scalar(select(func.count(Level.id))) or 0

    by_level = {}
    for lv in db.scalars(select(Level).order_by(Level.orden)).all():
        tot = (
            db.scalar(
                select(func.count(Lesson.id))
                .join(Course, Course.id == Lesson.course_id)
                .where(Course.level_id == lv.id)
            )
            or 0
        )
        done = (
            db.scalar(
                select(func.count(Progreso.id))
                .join(Lesson, Lesson.id == Progreso.lesson_id)
                .join(Course, Course.id == Lesson.course_id)
                .where(Progreso.user_id == current.id, Course.level_id == lv.id)
            )
            or 0
        )
        by_level[lv.code] = {"total": tot, "completadas": done}

    completadas_set = list(completadas)
    return {
        "total_lecciones": total_lecciones,
        "total_niveles": total_niveles,
        "completadas": len(completadas_set),
        "porcentaje": round((len(completadas_set) / total_lecciones * 100), 1) if total_lecciones else 0,
        "by_level": by_level,
        "lessons_done": completadas_set,
    }


@router.post("/membresia/activar", response_model=dict)
def activar_membresia(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    current.is_premium = True
    current.plan = "premium"
    db.commit()
    return {"ok": True, "plan": current.plan, "is_premium": current.is_premium}


@router.post("/membresia/cancelar", response_model=dict)
def cancelar_membresia(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    current.is_premium = False
    current.plan = "free"
    db.commit()
    return {"ok": True, "plan": current.plan, "is_premium": current.is_premium}


@router.get("/membresia", response_model=dict)
def estado_membresia(current: User = Depends(get_current_user)):
    return {
        "plan": current.plan,
        "is_premium": current.is_premium,
        "precio_mensual": 9.99,
    }


class SolicitudIn(BaseModel):
    to_id: int


@router.post("/privado/solicitar", response_model=dict)
def solicitar_privado(
    data: SolicitudIn,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if data.to_id == current.id:
        raise HTTPException(status_code=400, detail="No puedes enviarte una solicitud a ti mismo")
    existing = db.scalar(
        select(SolicitudPrivada).where(
            (SolicitudPrivada.from_id == current.id) & (SolicitudPrivada.to_id == data.to_id)
        )
    )
    if not existing:
        existing = SolicitudPrivada(from_id=current.id, to_id=data.to_id, status="pending")
        db.add(existing)
        db.commit()
        db.refresh(existing)
    elif existing.status == "declined":
        existing.status = "pending"
        db.commit()
    return {"status": existing.status, "solicitud_id": existing.id}


@router.get("/privado/solicitudes", response_model=list[dict])
def listar_solicitudes(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    rows = db.scalars(
        select(SolicitudPrivada)
        .where((SolicitudPrivada.to_id == current.id) & (SolicitudPrivada.status == "pending"))
    ).all()
    out = []
    for r in rows:
        u = db.get(User, r.from_id)
        out.append({"id": r.id, "from_id": r.from_id, "from_nombre": u.nombre if u else "Usuario"})
    return out


@router.post("/privado/solicitudes/{sid}/aceptar", response_model=dict)
def aceptar_solicitud(
    sid: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    r = db.get(SolicitudPrivada, sid)
    if not r or r.to_id != current.id:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    r.status = "accepted"
    db.commit()
    try:
        import routers.private_chat as pc
        for ws in list(pc.private_conns.get(r.from_id, [])):
            try:
                ws.send_text(json.dumps({"type": "accepted", "peer": current.id}))
            except Exception:
                pass
    except Exception:
        pass
    return {"ok": True}


@router.post("/privado/solicitudes/{sid}/rechazar", response_model=dict)
def rechazar_solicitud(
    sid: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    r = db.get(SolicitudPrivada, sid)
    if not r or r.to_id != current.id:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    r.status = "declined"
    db.commit()
    return {"ok": True}


@router.get("/privado/estado", response_model=dict)
def estado_privado(
    peer_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    r = db.scalar(
        select(SolicitudPrivada).where(
            ((SolicitudPrivada.from_id == current.id) & (SolicitudPrivada.to_id == peer_id))
            | ((SolicitudPrivada.from_id == peer_id) & (SolicitudPrivada.to_id == current.id))
        )
    )
    if not r:
        return {"status": "none"}
    if r.status == "accepted":
        return {"status": "accepted"}
    return {"status": "pending", "from_me": r.from_id == current.id}


@router.get("/usuarios", response_model=list[dict])
def listar_usuarios(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    users = db.scalars(select(User).where(User.id != current.id)).all()
    return [{"id": u.id, "nombre": u.nombre} for u in users]


@router.get("/usuarios/buscar", response_model=list[dict])
def buscar_usuarios(
    q: str = "",
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not q or not q.strip():
        return []
    like = f"%{q.strip().lower()}%"
    users = db.scalars(
        select(User)
        .where(User.id != current.id)
        .where((func.lower(User.nombre).like(like)) | (func.lower(User.email).like(like)))
        .limit(20)
    ).all()
    return [{"id": u.id, "nombre": u.nombre} for u in users]


@router.get("/usuarios/{user_id}", response_model=dict)
def obtener_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    u = db.get(User, user_id)
    if not u or u.id == current.id:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id": u.id, "nombre": u.nombre, "email": u.email, "role": u.role}


@router.delete("/usuarios/{user_id}", response_model=dict)
def eliminar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Solo un administrador puede eliminar usuarios")
    if user_id == current.id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.execute(delete(PrivateMessage).where((PrivateMessage.user_id == user_id) | (PrivateMessage.peer_id == user_id)))
    db.execute(delete(Progreso).where(Progreso.user_id == user_id))
    db.execute(delete(ChatMessage).where(ChatMessage.user_id == user_id))
    db.execute(delete(TestResult).where(TestResult.user_id == user_id))
    db.delete(u)
    db.commit()
    return {"ok": True, "eliminado": user_id}
