import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import SessionLocal
from models import User, PrivateMessage, SolicitudPrivada
import auth_utils

router = APIRouter(tags=["chat-privado"])


# user_id -> lista de websockets conectados
private_conns: dict[int, list] = {}


def auth_token(token: str):
    try:
        payload = auth_utils.decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        return None
    db = SessionLocal()
    user = db.get(User, user_id)
    db.close()
    return user


def peer_online(peer_id: int):
    return peer_id in private_conns and len(private_conns[peer_id]) > 0


def request_accepted(a: int, b: int) -> bool:
    db = SessionLocal()
    try:
        row = db.scalar(
            select(SolicitudPrivada).where(
                ((SolicitudPrivada.from_id == a) & (SolicitudPrivada.to_id == b))
                | ((SolicitudPrivada.from_id == b) & (SolicitudPrivada.to_id == a))
            )
        )
        return bool(row and row.status == "accepted")
    finally:
        db.close()


async def deliver(user_id: int, payload: dict):
    for ws in list(private_conns.get(user_id, [])):
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            pass


@router.websocket("/api/chat/private/ws")
async def private_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")
    peer_id = websocket.query_params.get("peer")
    if not peer_id or not peer_id.isdigit():
        await websocket.close(code=1008)
        return
    peer_id = int(peer_id)

    user = auth_token(token)
    if not user or user.id == peer_id:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    me = user.id
    private_conns.setdefault(me, []).append(websocket)

    # historial entre ambos
    db = SessionLocal()
    history = db.scalars(
        select(PrivateMessage)
        .where(
            ((PrivateMessage.user_id == me) & (PrivateMessage.peer_id == peer_id))
            | ((PrivateMessage.user_id == peer_id) & (PrivateMessage.peer_id == me))
        )
        .order_by(PrivateMessage.created_at)
        .limit(100)
    ).all()
    db.close()
    for m in history:
        await websocket.send_text(json.dumps({
            "type": "msg",
            "from": m.user_id,
            "content": m.content,
        }))

    await websocket.send_text(json.dumps({"type": "status", "accepted": request_accepted(me, peer_id)}))

    await deliver(peer_id, {"type": "online", "peer": me, "online": True})

    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=10)
            except asyncio.TimeoutError:
                try:
                    await websocket.send_text(json.dumps({"type": "ping"}))
                except Exception:
                    break
                continue
            text = data.strip()
            if not text:
                continue
            if not request_accepted(me, peer_id):
                try:
                    await websocket.send_text(json.dumps({"type": "error", "message": "El chat aún no ha sido aceptado."}))
                except Exception:
                    pass
                continue
            db = SessionLocal()
            pm = PrivateMessage(
                user_id=me,
                peer_id=peer_id,
                sender_name=user.nombre,
                content=text,
            )
            db.add(pm)
            db.commit()
            db.close()
            payload = {"type": "msg", "from": me, "content": text}
            await deliver(me, payload)
            await deliver(peer_id, payload)
    except WebSocketDisconnect:
        if me in private_conns and websocket in private_conns[me]:
            private_conns[me].remove(websocket)
        if me in private_conns and len(private_conns[me]) == 0:
            del private_conns[me]
        await deliver(peer_id, {"type": "online", "peer": me, "online": False})
