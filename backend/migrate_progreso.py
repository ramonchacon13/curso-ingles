from database import engine, Base
from models import Progreso
from sqlalchemy import inspect


def migrate():
    inspector = inspect(engine)
    if "progreso" in inspector.get_table_names():
        print("La tabla progreso ya existe.")
        return
    Progreso.__table__.create(engine, checkfirst=True)
    print("Tabla progreso creada.")


if __name__ == "__main__":
    migrate()
