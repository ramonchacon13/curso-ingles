from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import User, Progreso, Lesson, Level, Course
from auth_deps import get_current_user
from auth_utils import hash_password, verify_password
from sqlalchemy import select, func

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


@router.get("/usuarios", response_model=list[dict])
def listar_usuarios(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    users = db.scalars(select(User).where(User.id != current.id)).all()
    return [{"id": u.id, "nombre": u.nombre} for u in users]
