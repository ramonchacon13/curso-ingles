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


@app.get("/api/debug")
def debug():
    import os
    import re
    raw = os.environ.get("DATABASE_URL", "(no definido)")
    masked = re.sub(r'(://[^:]+:)[^@]+(@)', r'\1***\2', raw)
    return {"database_url": masked}


try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"AVISO: create_all falló ({e})")


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
    except Exception as e:
        print(f"AVISO: no se pudo sembrar en este arranque ({e}).")


import threading
threading.Thread(target=_seed_if_empty, daemon=True).start()
