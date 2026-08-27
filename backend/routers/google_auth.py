import os
from urllib.parse import quote
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth

from database import get_db
from models import User
from auth_utils import create_token, hash_password
from config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, FRONTEND_URL,
)
from mail import send_welcome

router = APIRouter(prefix="/api/auth", tags=["auth-google"])

oauth = OAuth()
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


def _frontend():
    return FRONTEND_URL.rstrip("/") if FRONTEND_URL else ""


@router.get("/google/login")
async def google_login(request: Request):
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        return RedirectResponse(f"{_frontend()}/login?error=oauth_disabled")
    host = request.headers.get("host") or request.url.hostname
    scheme = request.headers.get("x-forwarded-proto") or request.url.scheme
    redirect_uri = f"{scheme}://{host}/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    fx = _frontend()
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        return RedirectResponse(f"{fx}/login?error=oauth_disabled")

    gerr = request.query_params.get("error")
    if gerr:
        desc = request.query_params.get("error_description", "")
        print("GOOGLE_OAUTH_ERROR:", gerr, desc)
        return RedirectResponse(f"{fx}/login?error=oauth&reason={quote(gerr)}")

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        print("GOOGLE_OAUTH_EXCEPTION:", repr(e))
        return RedirectResponse(f"{fx}/login?error=oauth&reason=token_exchange")

    userinfo = token.get("userinfo")
    if not userinfo:
        try:
            resp = await oauth.google.userinfo(token=token)
            userinfo = resp.json()
        except Exception:
            userinfo = {}

    email = (userinfo.get("email") or "").strip().lower()
    if not email or userinfo.get("email_verified") is False:
        return RedirectResponse(f"{fx}/login?error=oauth_email")

    name = userinfo.get("name") or email.split("@")[0]
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            nombre=name,
            hashed_password=hash_password(os.urandom(16).hex()),
            nivel="A1",
            is_premium=False,
            plan="free",
            role="user",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        try:
            send_welcome(user.email, user.nombre)
        except Exception:
            pass

    jwt = create_token(user.id)
    return RedirectResponse(f"{fx}/oauth-callback?token={jwt}")
