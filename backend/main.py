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


Base.metadata.create_all(bind=engine)
