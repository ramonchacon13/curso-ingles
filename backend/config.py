import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres@localhost:5433/curso_ingles")

JWT_SECRET = os.getenv("JWT_SECRET", "cambiame-por-un-secreto-seguro")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v3")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

APP_NAME = "CursoIngles API"

# Lista de correos (separados por coma) que tendrán rol de administrador.
# Se aplican al arranque. Para añadir moderadores, asígnales el rol manualmente
# desde el panel/admin o vía BD; el sistema ya soporta múltiples moderadores.
ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "")

# URLs públicas del sitio (para redirecciones OAuth y correos)
API_BASE_URL = os.getenv("API_BASE_URL", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "")

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
SESSION_SECRET = os.getenv("SESSION_SECRET", JWT_SECRET)
