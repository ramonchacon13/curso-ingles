import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
import models
from models import Level, Course, Lesson, Test, Question

Base.metadata.create_all(bind=engine)

db = SessionLocal()

if db.query(Level).first():
    print("Ya existen datos. Saltando seed.")
    db.close()
    sys.exit(0)

levels_data = [
    ("A1", "Nivel Básico", "Para quienes empiezan desde cero.", 1),
    ("A2", "Nivel Elemental", "Conceptos básicos y frases cotidianas.", 2),
    ("B1", "Nivel Intermedio", "Comunicación en situaciones familiares.", 3),
    ("B2", "Nivel Avanzado", "Inglés fluido en contextos variados.", 4),
    ("C1", "Nivel Proficiencia", "Uso flexible y efectivo del idioma.", 5),
    ("C2", "Nivel Maestría", "Comprensión y expresión como nativo.", 6),
]

level_objs = {}
for code, name, desc, orden in levels_data:
    lvl = Level(code=code, name=name, description=desc, orden=orden)
    db.add(lvl)
    db.flush()
    level_objs[code] = lvl

courses_data = {
    "A1": [
        ("Primeros pasos", "Saludos, presentarte y el alfabeto.", False),
        ("Pronombres personales", "I, you, he, she, it, we, they.", False),
        ("El presente simple", "Verbos en presente y estructura básica.", False),
        ("Vocabulario esencial", "Palabras del día a día (premium).", True),
    ],
    "A2": [
        ("El pasado simple", "Verbos regulares e irregulares en pasado.", False),
        ("El futuro", "Going to y will.", False),
    ],
    "B1": [
        ("Presente continuo", "Acciones en progreso.", False),
        ("Comparativos y superlativos", "Estructuras de comparación.", False),
    ],
    "B2": [
        ("Condicionales", "First, second y third conditional.", False),
        ("Voz pasiva", "Formación y usos.", False),
    ],
    "C1": [
        ("Phrasal verbs avanzados", "Combinaciones frecuentes.", True),
        ("Expresiones idiomáticas", "Modismos y coloquialismos.", True),
    ],
    "C2": [
        ("Inglés académico", "Registro formal y ensayo.", True),
    ],
}

lesson_samples = [
    ("Saludos básicos", "Hello! / Hi! / Good morning. My name is... Nice to meet you.", False),
    ("Presentación", "I am from Spain. I live in Madrid. I am a student.", False),
    ("El verbo to be", "I am, you are, he is, we are, they are. Negativo: I am not.", False),
]

for code, courses in courses_data.items():
    lvl = level_objs[code]
    for i, (title, desc, prem) in enumerate(courses, start=1):
        course = Course(level_id=lvl.id, title=title, description=desc, orden=i)
        db.add(course)
        db.flush()
        for j, (ltitle, lcontent, lprem) in enumerate(lesson_samples, start=1):
            db.add(Lesson(
                course_id=course.id,
                title=ltitle,
                content=lcontent,
                orden=j,
                is_premium=prem,
            ))

tests_data = {
    "A1": ("Test de Nivel Básico", [
        ("¿Cómo se dice 'yo soy' en inglés?", ["I am", "I is", "I are"], 0, "El verbo to be en primera persona es 'I am'."),
        ("¿Cuál es el pronombre para 'ella'?", ["he", "she", "it"], 1, "'She' significa ella."),
        ("'Cat' significa...", ["perro", "gato", "pájaro"], 1, "Cat = gato."),
    ]),
}

for code, (ttitle, questions) in tests_data.items():
    lvl = level_objs[code]
    test = Test(level_id=lvl.id, title=ttitle)
    db.add(test)
    db.flush()
    for prompt, options, correct, explanation in questions:
        db.add(Question(
            test_id=test.id,
            prompt=prompt,
            options=options,
            correct=correct,
            explanation=explanation,
        ))

db.commit()
print("Seed completado: niveles, cursos, lecciones y tests creados.")
db.close()
