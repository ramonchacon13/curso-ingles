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

app.include_router(auth.router, prefix="/api/auth")
app.include_router(courses.router, prefix="/api")
app.include_router(chat.router)
app.include_router(tests.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(private_chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "CursoIngles"}


def _init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"AVISO: create_all falló ({e})")
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
    except Exception as e:
        print(f"AVISO: no se pudo sembrar en este arranque ({e}).")


import threading
threading.Thread(target=_init_db, daemon=True).start()
