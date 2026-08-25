from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from database import get_db
from models import User, Progreso, Lesson, Level, Course, PrivateMessage, ChatMessage, TestResult
from auth_deps import get_current_user, require_admin
from auth_utils import hash_password, verify_password
from sqlalchemy import select, func, delete
from fastapi.responses import Response
import base64

router = APIRouter(prefix="/api", tags=["usuarios"])

NIVELES_VALIDOS = ["A1", "A2", "B1", "B2", "C1", "C2"]


class NivelUpdate(BaseModel):
    nivel: str


class PerfilUpdate(BaseModel):
    nombre: str | None = None
    email: str | None = None
    email_opt_in: bool | None = None
    avatar_kind: str | None = None
    avatar_value: str | None = None


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
    if data.avatar_kind is not None:
        kind = data.avatar_kind
        if kind not in ("initials", "emoji", "image"):
            raise HTTPException(status_code=400, detail="Tipo de avatar inválido")
        if kind == "image":
            val = data.avatar_value
            if not val or not str(val).startswith("data:image/"):
                raise HTTPException(status_code=400, detail="Debes proporcionar una imagen válida")
            if len(val) > 300000:
                raise HTTPException(status_code=400, detail="Imagen demasiado grande (máx ~300KB)")
            current.avatar_value = val
        elif kind == "emoji":
            val = data.avatar_value
            if not val or len(str(val)) > 8:
                raise HTTPException(status_code=400, detail="Emoji inválido")
            current.avatar_value = str(val)
        else:
            current.avatar_value = None
        current.avatar_kind = kind
    db.commit()
    return {
        "ok": True,
        "nombre": current.nombre,
        "email": current.email,
        "email_opt_in": current.email_opt_in,
        "avatar_kind": current.avatar_kind,
        "avatar_value": current.avatar_value,
    }


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


@router.get("/usuarios", response_model=list[dict])
def listar_usuarios(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    users = db.scalars(select(User).where(User.id != current.id)).all()
    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "avatar_kind": u.avatar_kind or "initials",
            "avatar_value": (u.avatar_value if u.avatar_kind != "image" else None),
        }
        for u in users
    ]


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
    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "avatar_kind": u.avatar_kind or "initials",
            "avatar_value": (u.avatar_value if u.avatar_kind != "image" else None),
        }
        for u in users
    ]


@router.get("/usuarios/{user_id}", response_model=dict)
def obtener_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    u = db.get(User, user_id)
    if not u or u.id == current.id:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "id": u.id,
        "nombre": u.nombre,
        "email": u.email,
        "role": u.role,
        "avatar_kind": u.avatar_kind or "initials",
        "avatar_value": u.avatar_value,
    }


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
    try:
        db.execute(delete(PrivateMessage).where((PrivateMessage.user_id == user_id) | (PrivateMessage.peer_id == user_id)))
        db.execute(delete(Progreso).where(Progreso.user_id == user_id))
        db.execute(delete(ChatMessage).where(ChatMessage.user_id == user_id))
        db.execute(delete(TestResult).where(TestResult.user_id == user_id))
        db.delete(u)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"No se pudo eliminar el usuario: {str(e)[:200]}")
    return {"ok": True, "eliminado": user_id}


@router.delete("/admin/usuarios", response_model=dict)
def admin_eliminar_todos(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    no_admin = select(User.id).where(User.role != "admin")
    try:
        db.execute(
            delete(PrivateMessage).where(
                PrivateMessage.user_id.in_(no_admin) | PrivateMessage.peer_id.in_(no_admin)
            )
        )
        db.execute(delete(Progreso).where(Progreso.user_id.in_(no_admin)))
        db.execute(delete(ChatMessage).where(ChatMessage.user_id.in_(no_admin)))
        db.execute(delete(TestResult).where(TestResult.user_id.in_(no_admin)))
        res = db.execute(delete(User).where(User.role != "admin"))
        db.commit()
        return {"ok": True, "eliminados": res.rowcount}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"No se pudo eliminar: {str(e)[:200]}")


def _serialize(u):
    return {
        "id": u.id,
        "nombre": u.nombre,
        "email": u.email,
        "role": u.role,
        "nivel": u.nivel,
        "is_premium": u.is_premium,
        "plan": u.plan,
        "email_opt_in": u.email_opt_in,
        "avatar_kind": u.avatar_kind or "initials",
        "avatar_value": u.avatar_value,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


@router.get("/admin/usuarios", response_model=dict)
def admin_listar_usuarios(
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    page = max(1, page)
    limit = min(max(1, limit), 500)
    offset = (page - 1) * limit
    total = db.scalar(select(func.count(User.id))) or 0
    usuarios = db.scalars(
        select(User).order_by(User.id).offset(offset).limit(limit)
    ).all()
    return {"items": [_serialize(u) for u in usuarios], "total": total, "page": page, "limit": limit}


@router.get("/admin/usuarios/buscar", response_model=list[dict])
def admin_buscar_usuarios(
    q: str = "",
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if not q or not q.strip():
        return []
    like = f"%{q.strip().lower()}%"
    usuarios = db.scalars(
        select(User)
        .where((func.lower(User.nombre).like(like)) | (func.lower(User.email).like(like)))
        .order_by(User.id)
        .limit(200)
    ).all()
    return [_serialize(u) for u in usuarios]


class AdminUserUpdate(BaseModel):
    nombre: str | None = None
    email: str | None = None
    role: str | None = None
    nivel: str | None = None
    is_premium: bool | None = None


@router.put("/admin/usuarios/{user_id}", response_model=dict)
def admin_actualizar_usuario(
    user_id: int,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if data.nombre is not None and data.nombre.strip():
        u.nombre = data.nombre.strip()

    if data.email is not None and data.email.strip():
        nuevo = data.email.strip().lower()
        if nuevo != u.email:
            existe = db.scalar(
                select(User).where(func.lower(User.email) == nuevo, User.id != u.id)
            )
            if existe:
                raise HTTPException(status_code=400, detail="El correo ya está registrado")
            u.email = nuevo

    if data.role is not None:
        if data.role not in ("user", "admin", "moderator"):
            raise HTTPException(status_code=400, detail="Rol inválido")
        u.role = data.role

    if data.nivel is not None:
        if data.nivel not in NIVELES_VALIDOS:
            raise HTTPException(status_code=400, detail="Nivel inválido")
        u.nivel = data.nivel

    if data.is_premium is not None:
        u.is_premium = bool(data.is_premium)
        u.plan = "premium" if u.is_premium else "free"

    db.commit()
    return _serialize(u)


@router.get("/usuarios/{user_id}/avatar")
def obtener_avatar(user_id: int, db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u or u.avatar_kind != "image" or not u.avatar_value or not str(u.avatar_value).startswith("data:image/"):
        raise HTTPException(status_code=404, detail="Sin avatar")
    try:
        header, b64 = u.avatar_value.split(",", 1)
        raw = base64.b64decode(b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Avatar inválido")
    media = "image/png"
    if "jpeg" in header or "jpg" in header:
        media = "image/jpeg"
    elif "webp" in header:
        media = "image/webp"
    return Response(content=raw, media_type=media)
