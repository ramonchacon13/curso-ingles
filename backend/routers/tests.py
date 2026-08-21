from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from models import User, Level, Test, Question, TestResult
from schemas import TestOut, TestSubmit, TestResultOut
from auth_deps import get_current_user

router = APIRouter(prefix="/api", tags=["tests"])

UMBRAL_NIVEL = 0.6  # 60% para aprobar y asignar el nivel


@router.get("/niveles/{level_code}/tests", response_model=list[TestOut])
def list_tests(level_code: str, db: Session = Depends(get_db)):
    level = db.scalar(select(Level).where(Level.code == level_code))
    if not level:
        raise HTTPException(status_code=404, detail="Nivel no encontrado")
    tests = db.scalars(select(Test).where(Test.level_id == level.id)).all()
    for t in tests:
        t.questions = db.scalars(
            select(Question).where(Question.test_id == t.id)
        ).all()
    return tests


@router.post("/tests/submit", response_model=TestResultOut)
def submit_test(
    data: TestSubmit,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    test = db.get(Test, data.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test no encontrado")
    questions = db.scalars(select(Question).where(Question.test_id == test.id)).all()
    total = len(questions)
    if len(data.answers) != total:
        raise HTTPException(status_code=400, detail="Faltan respuestas")
    score = sum(1 for q, a in zip(questions, data.answers) if q.correct == a)

    result = TestResult(
        user_id=current.id, test_id=test.id, score=score, total=total
    )
    db.add(result)

    nivel_actualizado = False
    ratio = score / total if total else 0
    level = db.get(Level, test.level_id)
    if level and ratio >= UMBRAL_NIVEL:
        current.nivel = level.code
        nivel_actualizado = True

    db.commit()
    db.refresh(result)
    return TestResultOut(
        test_id=result.test_id,
        score=result.score,
        total=result.total,
        completed_at=result.completed_at.isoformat(),
        nivel_actualizado=nivel_actualizado,
        nivel=current.nivel,
    )
