from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, courses, chat, tests, users, private_chat
from database import engine, Base
import models

app = FastAPI(title="CursoIngles API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(chat.router)
app.include_router(tests.router)
app.include_router(users.router)
app.include_router(private_chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "CursoIngles"}


try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"AVISO: create_all falló ({e})")


def _patch_schema():
    from database import SessionLocal
    from sqlalchemy import select, text
    import models
    from config import ADMIN_EMAILS
    db = SessionLocal()
    try:
        # Añade columna role si no existe (idempotente y seguro en sqlite/postgres)
        try:
            db.execute(text("ALTER TABLE usuarios ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"))
            db.commit()
        except Exception:
            db.rollback()
        # Asigna rol admin a los correos configurados en ADMIN_EMAILS
        emails = [e.strip().lower() for e in (ADMIN_EMAILS or "").split(",") if e.strip()]
        if emails:
            users = db.scalars(select(models.User).where(models.User.email.in_(emails))).all()
            for u in users:
                u.role = "admin"
            db.commit()
            print(f"Admin(s) configurado(s): {[u.email for u in users]}")
    except Exception as e:
        print(f"AVISO _patch_schema: {e}")
    finally:
        db.close()


try:
    _patch_schema()
except Exception as e:
    print(f"AVISO _patch_schema arranque: {e}")


def _seed_if_empty():
    try:
        from sqlalchemy import func, select
        from database import SessionLocal
        import models
        with SessionLocal() as db:
            if db.scalar(select(func.count(models.Level.id))) == 0:
                import subprocess, sys
                print("BD vacía: sembrando contenido inicial...")
                subprocess.run([sys.executable, "seed_content.py"], check=True)
                print("Seed completado.")
        # Asegura 20 preguntas por nivel (solo agrega, no borra registros)
        from migrate_questions import ensure_20_questions
        ensure_20_questions()
    except Exception as e:
        print(f"AVISO: no se pudo sembrar/completar en este arranque ({e}).")


import threading
threading.Thread(target=_seed_if_empty, daemon=True).start()
