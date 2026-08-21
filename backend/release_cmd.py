import subprocess
import sys

from database import SessionLocal, engine
import models
from sqlalchemy import func, select

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()
niveles = db.scalar(select(func.count(models.Level.id)))
db.close()

if niveles == 0:
    print("BD vacía: sembrando contenido inicial...")
    subprocess.run([sys.executable, "seed_content.py"], check=True)
else:
    print("BD ya tiene contenido, se omite el seed.")

print("init_data completado.")
