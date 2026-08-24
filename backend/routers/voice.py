import io

import edge_tts
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter(prefix="/api/voice", tags=["voice"])


class TTSRequest(BaseModel):
    text: str
    voice: str = "en-US-AriaNeural"


def _normalize(voices):
    if isinstance(voices, dict) and "VoiceList" in voices:
        return voices["VoiceList"]
    return voices


@router.get("/voices")
async def list_voices():
    try:
        raw = await edge_tts.list_voices()
    except Exception as e:
        raise HTTPException(502, f"No se pudieron listar las voces: {e}")
    items = _normalize(raw)
    out = []
    for v in items:
        short = v.get("ShortName") or v.get("Name")
        locale = v.get("Locale") or ""
        if not short:
            continue
        if "Neural" not in short:
            continue
        if not (locale.startswith("en") or locale.startswith("es")):
            continue
        out.append({"name": short, "locale": locale, "gender": v.get("Gender", "")})
    out.sort(key=lambda x: x["name"])
    return out


@router.post("/tts")
async def tts(req: TTSRequest):
    if not req.text or len(req.text) > 1000:
        raise HTTPException(400, "Texto inválido o demasiado largo")
    try:
        communicate = edge_tts.Communicate(req.text, req.voice)
        buf = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk.get("type") == "audio":
                buf.write(chunk["data"])
        data = buf.getvalue()
        if not data:
            raise HTTPException(502, "No se generó audio")
        return Response(content=data, media_type="audio/mpeg")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, f"Error de síntesis: {e}")
