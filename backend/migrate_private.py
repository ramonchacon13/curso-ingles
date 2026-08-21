import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import engine, Base
import models

models.PrivateMessage.__table__.create(engine, checkfirst=True)
print("Tabla mensajes_privados lista.")
