import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import SessionLocal
from models import User, PrivateMessage
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

    await deliver(peer_id, {"type": "online", "peer": me, "online": True})

    try:
        while True:
            data = await websocket.receive_text()
            text = data.strip()
            if not text:
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
