import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from models import User
from auth_deps import get_current_user
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL

router = APIRouter(prefix="/api/ai", tags=["ai"])

SYSTEM_PROMPT = (
    "Eres un tutor de inglés amigable para personas hispanohablantes que están aprendiendo. "
    "Tu objetivo es que practiquen hablando, sin presión. Reglas:\n"
    "- Responde en inglés, frases CORTAS (1 a 3 oraciones), lenguaje sencillo.\n"
    "- Sé alentador y cercano (usa emojis ocasionales como 😊🎉).\n"
    "- Corrige suaves y brevemente solo si es necesario; nunca regañes.\n"
    "- Haz una pregunta corta al final para que la conversación siga fluyendo.\n"
    "- Si el estudiante se traba o pide ayuda en español, ayúdalo en español sin problemas.\n"
    "Mantén siempre un tono divertido y ligero, nunca tedioso."
)


class TutorMessage(BaseModel):
    role: str
    content: str


class TutorRequest(BaseModel):
    history: Optional[List[TutorMessage]] = []
    message: str


@router.post("/tutor")
async def tutor(
    data: TutorRequest,
    current: User = Depends(get_current_user),
):
    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="El servicio de tutor de voz no está configurado en este momento.",
        )

    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in (data.history or [])[-12:]:
        if h.role in ("user", "assistant"):
            msgs.append({"role": h.role, "content": h.content})
    msgs.append({"role": "user", "content": data.message})

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                OPENROUTER_BASE_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": msgs,
                    "temperature": 0.8,
                    "max_tokens": 220,
                },
            )
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail="No pude conectar con el tutor en este momento. Inténtalo de nuevo.",
        )

    return {"reply": reply}
