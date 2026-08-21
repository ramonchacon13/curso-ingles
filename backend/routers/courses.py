from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from models import Level, Course, Lesson, Progreso
from schemas import LevelOut, CourseOut, LessonOut
from auth_deps import get_current_user
from models import User

router = APIRouter(prefix="/api", tags=["cursos"])


@router.get("/niveles", response_model=list[LevelOut])
def list_levels(db: Session = Depends(get_db)):
    return db.scalars(select(Level).order_by(Level.orden)).all()


@router.get("/niveles/{level_code}/cursos", response_model=list[CourseOut])
def list_courses(level_code: str, db: Session = Depends(get_db)):
    level = db.scalar(select(Level).where(Level.code == level_code))
    if not level:
        raise HTTPException(status_code=404, detail="Nivel no encontrado")
    courses = db.scalars(
        select(Course).where(Course.level_id == level.id).order_by(Course.orden)
    ).all()
    for c in courses:
        c.lessons = db.scalars(
            select(Lesson).where(Lesson.course_id == c.id).order_by(Lesson.orden)
        ).all()
    return courses


@router.get("/lecciones/{lesson_id}", response_model=LessonOut)
def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lección no encontrada")
    if lesson.is_premium and not current.is_premium:
        raise HTTPException(status_code=403, detail="Esta lección es solo para miembros premium")
    return lesson


@router.post("/lecciones/{lesson_id}/completar", response_model=dict)
def completar_leccion(
    lesson_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lección no encontrada")
    existente = db.scalar(
        select(Progreso).where(Progreso.user_id == current.id, Progreso.lesson_id == lesson_id)
    )
    if existente:
        db.delete(existente)
        db.commit()
        return {"ok": True, "completada": False}
    db.add(Progreso(user_id=current.id, lesson_id=lesson_id))
    db.commit()
    return {"ok": True, "completada": True}
