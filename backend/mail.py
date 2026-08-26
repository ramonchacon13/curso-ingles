import os
import smtplib
import ssl
from email.message import EmailMessage

MAIL_HOST = os.getenv("MAIL_HOST", "")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USER = os.getenv("MAIL_USER", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", "Best English <no-reply@bestenglish.com>")

PRIMARY = "#6c5ce7"
PRIMARY_DARK = "#4b3fd1"


def _wrap(title, body_html):
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="margin:0;background:#f4f6fb;font-family:Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
  <div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.06);">
    <div style="background:linear-gradient(135deg,{PRIMARY},{PRIMARY_DARK});padding:22px 26px;color:#fff;">
      <h1 style="margin:0;font-size:20px;">Curso<span style="font-weight:800;">Inglés</span></h1>
    </div>
    <div style="padding:26px;color:#2c2c2c;">
      <h2 style="margin:0 0 12px;font-size:18px;">{title}</h2>
      {body_html}
    </div>
    <div style="padding:16px 26px;background:#fafbff;color:#8a94a6;font-size:12px;border-top:1px solid #eef1f6;">
      Recibes este correo de Best English. Si no quieres recibir resúmenes, puedes desactivarlos en tu perfil.
    </div>
  </div>
</body>
</html>"""


def send_email(to, subject, html):
    if not (MAIL_HOST and MAIL_PASSWORD and MAIL_FROM):
        print("AVISO: correo no enviado (MAIL_* no configurado).")
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = MAIL_FROM
        msg["To"] = to
        msg.set_content("Este correo requiere un cliente con HTML.")
        msg.add_alternative(html, subtype="html")
        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as s:
            s.starttls(context=ssl.create_default_context())
            s.login(MAIL_USER or MAIL_FROM, MAIL_PASSWORD)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f"AVISO: fallo al enviar correo a {to}: {e}")
        return False


def send_welcome(to, name):
    body = f"""
      <p>Hola <b>{name or 'estudiante'}</b>, ¡bienvenido a <b>Best English</b>! 🎉</p>
      <p>Ya puedes practicar inglés gratis: lecciones, tests y un chat con la comunidad.</p>
      <p style="margin-top:18px;"><a href="{os.getenv('FRONTEND_URL', '')}/cursos"
         style="background:{PRIMARY};color:#fff;padding:11px 18px;border-radius:10px;text-decoration:none;font-weight:600;">Empezar ahora</a></p>
    """
    return send_email(to, "¡Bienvenido a Best English! 🎉", _wrap("Bienvenido 👋", body))


def send_password_reset(to, name, link):
    body = f"""
      <p>Hola <b>{name or 'estudiante'}</b>, recibimos una solicitud para restablecer tu contraseña.</p>
      <p style="margin-top:18px;"><a href="{link}"
         style="background:{PRIMARY};color:#fff;padding:11px 18px;border-radius:10px;text-decoration:none;font-weight:600;">Cambiar contraseña</a></p>
      <p style="color:#8a94a6;font-size:13px;">Si no fuiste tú, ignora este correo. El enlace expira pronto.</p>
    """
    return send_email(to, "Restablece tu contraseña", _wrap("Seguridad 🔒", body))


def send_weekly_progress(to, name, data):
    body = f"""
      <p>Hola <b>{name or 'estudiante'}</b>, este es tu resumen semanal 📈</p>
      <ul style="line-height:1.7;">
        <li>Nivel actual: <b>{data.get('nivel', 'A1')}</b></li>
        <li>Lecciones completadas: <b>{data.get('completadas', 0)}</b></li>
        <li>Tests aprobados: <b>{data.get('tests', 0)}</b></li>
      </ul>
      <p style="margin-top:18px;"><a href="{os.getenv('FRONTEND_URL', '')}/dashboard"
         style="background:{PRIMARY};color:#fff;padding:11px 18px;border-radius:10px;text-decoration:none;font-weight:600;">Ver mi progreso</a></p>
    """
    return send_email(to, "Tu resumen semanal de Best English", _wrap("Resumen semanal 📈", body))


def send_premium_expiry(to, name, days):
    body = f"""
      <p>Hola <b>{name or 'estudiante'}</b>, tu plan premium expira en <b>{days} día(s)</b>. ⏳</p>
      <p>Sigue disfrutando del tutor de voz y todas las ventajas premium.</p>
      <p style="margin-top:18px;"><a href="{os.getenv('FRONTEND_URL', '')}/membresia"
         style="background:{PRIMARY};color:#fff;padding:11px 18px;border-radius:10px;text-decoration:none;font-weight:600;">Renovar plan</a></p>
    """
    return send_email(to, "Tu plan premium está por vencer", _wrap("Renueva tu plan ✨", body))
