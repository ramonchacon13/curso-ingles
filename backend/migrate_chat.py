import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import engine, Base
import models

models.ChatMessage.__table__.drop(engine, checkfirst=True)
Base.metadata.create_all(bind=engine)
print("Tabla chat_mensajes recreada con sender_name.")
