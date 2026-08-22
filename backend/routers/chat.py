import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import SessionLocal
from models import User, ChatMessage
import auth_utils

router = APIRouter(tags=["chat"])


class Conn:
    def __init__(self, ws, user):
        self.ws = ws
        self.user = user


connections: list[Conn] = []


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


async def broadcast(payload: dict):
    dead = []
    for c in list(connections):
        try:
            await c.ws.send_text(json.dumps(payload))
        except Exception:
            dead.append(c)
    for c in dead:
        if c in connections:
            connections.remove(c)


async def broadcast_online():
    await broadcast({"type": "online", "count": len(connections)})


@router.websocket("/api/chat/ws")
async def chat_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user = auth_token(token)
    if not user:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    db = SessionLocal()
    history = db.scalars(
        select(ChatMessage).order_by(ChatMessage.created_at).limit(50)
    ).all()
    db.close()
    for m in history:
        await websocket.send_text(json.dumps({
            "type": "msg",
            "user": m.sender_name,
            "content": m.content,
            "time": m.created_at.isoformat(),
        }))

    conn = Conn(websocket, user)
    connections.append(conn)
    await broadcast_online()

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
            db = SessionLocal()
            cm = ChatMessage(
                user_id=user.id,
                sender_name=user.nombre,
                role="user",
                content=text,
            )
            db.add(cm)
            db.commit()
            db.close()
            await broadcast({
                "type": "msg",
                "user": user.nombre,
                "content": text,
            })
    except WebSocketDisconnect:
        if conn in connections:
            connections.remove(conn)
        await broadcast_online()
