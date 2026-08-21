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
