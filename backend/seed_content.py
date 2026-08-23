import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal, engine
import models
from models import Level, Course, Lesson, Test, Question
from sqlalchemy import text

db = SessionLocal()

db.execute(text("DELETE FROM resultados_test"))
db.execute(text("DELETE FROM preguntas"))
db.execute(text("DELETE FROM tests"))
db.execute(text("DELETE FROM lecciones"))
db.execute(text("DELETE FROM cursos"))
db.execute(text("DELETE FROM niveles"))
db.commit()

level_objs = {}
for code, name, desc, orden in [
    ("A1", "Nivel Básico", "Para quienes empiezan desde cero.", 1),
    ("A2", "Nivel Elemental", "Frases cotidianas y gramática básica.", 2),
    ("B1", "Nivel Intermedio", "Comunicación en situaciones familiares.", 3),
    ("B2", "Nivel Avanzado", "Inglés fluido en contextos variados.", 4),
    ("C1", "Nivel Proficiencia", "Uso flexible y efectivo del idioma.", 5),
    ("C2", "Nivel Maestría", "Comprensión y expresión como nativo.", 6),
]:
    lvl = Level(code=code, name=name, description=desc, orden=orden)
    db.add(lvl); db.flush(); level_objs[code] = lvl

# (curso, descripcion, [(leccion, contenido, premium?)])
content = {
    "A1": [
        ("Saludos y presentaciones", "Saluda y preséntate.", [
            ("Cómo saludar", "Hello / Hi / Good morning. Nice to meet you.\nEj: Hi! I'm Ramón. Nice to meet you.", False),
            ("El verbo to be (ser/estar)", "I am, you are, he is, she is, it is, we are, they are.\nNegativo: I am not / he isn't.\nPregunta: Are you...? Yes, I am.", False),
            ("Países y nacionalidades", "I am from Spain. She is Mexican. They are from Colombia.\nNationalities: Spanish, Mexican, Colombian.", False),
            ("Decir tu edad y profesión", "I am 25 years old. I am a student / a teacher / a doctor.", False),
        ]),
        ("Pronombres personales", "Los sujetos en inglés.", [
            ("I, you, he, she, it, we, they", "I = yo, you = tú, he = él, she = ella, it = eso, we = nosotros, they = ellos.\nEj: She speaks English.", False),
            ("Pronombres objeto", "me, you, him, her, it, us, them.\nEj: The teacher helps me.", False),
            ("Posesivos", "my, your, his, her, its, our, their.\nEj: This is my book / their house.", False),
        ]),
        ("El presente simple", "Hábitos y rutinas.", [
            ("Formación", "Verbo base + -s en 3ª persona: I work / he works.\nNegativo con do/does: I don't like / he doesn't like.\nPregunta: Do you speak English?", False),
            ("Adverbios de frecuencia", "always, usually, often, sometimes, never.\nEj: I usually drink coffee.", False),
            ("Verbos 'like / love / hate'", "I like reading. She loves music. He hates spiders.\n+ gerundio o sustantivo.", False),
        ]),
        ("Vocabulario esencial", "Palabras clave del día a día.", [
            ("La familia", "mother, father, brother, sister, parents, children.\nEj: This is my brother.", True),
            ("Los números 1-100", "one, two, three... ten, twenty, thirty... one hundred.\nEj: I have two brothers.", True),
            ("Comida y bebida", "water, milk, bread, rice, fruit, vegetables.\nEj: I eat rice and vegetables.", True),
            ("Los días y meses", "Monday-Sunday, January-December.\nEj: Today is Monday. My birthday is in July.", True),
            ("Colores y objetos", "red, blue, green, black, white. book, table, chair, door.\nEj: The blue book is on the table.", True),
        ]),
    ],
    "A2": [
        ("El pasado simple", "Acciones terminadas.", [
            ("Verbos regulares", "worked, played, listened (verbo + -ed).\nEj: I played football yesterday.", False),
            ("Verbos irregulares", "go -> went, eat -> ate, see -> saw, have -> had.\nEj: She went to school.", False),
            ("Wh- questions", "What did you do? Where did he go? When did they arrive?", False),
            ("Expresiones de tiempo", "yesterday, last week, two days ago, in 2020.", False),
        ]),
        ("El futuro", "Planes y predicciones.", [
            ("Going to", "I am going to travel next month.\nPara planes: What are you going to do?", False),
            ("Will", "I will help you. It will rain tomorrow.\nPara decisiones rápidas y predicciones.", False),
            ("Time expressions futuro", "tomorrow, next week, soon, in a year.", False),
        ]),
        ("Preposiciones de lugar", "In, on, at, under, next to.", [
            ("In / On / At", "in the box, on the table, at school, under the bed.\nEj: The book is on the table.", False),
            ("Preposiciones de movimiento", "to, from, into, out of.\nEj: I go to school / She came from Paris.", True),
        ]),
        ("Descripciones y adjetivos", "Hablar de personas y cosas.", [
            ("Adjetivos comunes", "big, small, happy, tired, interesting, expensive.\nEj: The film is interesting.", True),
            ("Orden del adjetivo", "Opinión + tamaño + color: a small red car.", True),
        ]),
    ],
    "B1": [
        ("Presente continuo", "Acciones en este momento.", [
            ("Formación", "am/is/are + verbo -ing.\nI am studying. He is sleeping.\nvs presente simple: I study every day.", False),
            ("Estados vs acciones", "Verbos de estado (like, love, know) no usan -ing.\nEj: I like coffee (no 'I am liking').", False),
            ("Planes fijos (presente continuo)", "I am meeting him tomorrow. (Ej: el tren sale a las 8).", False),
        ]),
        ("Comparativos y superlativos", "Comparar cosas.", [
            ("Reglas", "Corto + -er/-est: small -> smaller -> smallest.\nLargos: more/most beautiful.\nIrregulares: good -> better -> best.", False),
            ("Ejemplos útiles", "This book is more interesting than that one.\nHe is the best student in class.", False),
            ("Much / Many / A lot of", "much (incontable), many (contable), a lot of (ambos).\nEj: much water / many friends.", False),
        ]),
        ("Pasado continuo", "Fondos y interrupciones.", [
            ("Estructura", "was/were + -ing. I was eating when you called.\nPara acción en progreso en el pasado.", False),
            ("While vs When", "While I was sleeping, the phone rang. When he arrived, we left.", True),
        ]),
        ("Modales de probabilidad", "Must, might, can't.", [
            ("Must / Might / Can't", "He must be tired (casi seguro). She might come (posible). He can't be here (casi imposible).", True),
        ]),
    ],
    "B2": [
        ("Condicionales", "Si pasa X, pasa Y.", [
            ("Zero / First", "If you heat water, it boils (zero). If it rains, I will stay (first).", False),
            ("Second / Third", "If I were rich, I would travel (second, hipotético).\nIf I had studied, I would have passed (third, pasado irrereal).", False),
            ("Mixed conditionals", "If I had studied (past), I would be calm now (present).", False),
        ]),
        ("Voz pasiva", "Poner el objeto primero.", [
            ("Formación", "be + participio: The book was written by him.\nPresente: is written. Pasado: was written.", False),
            ("Cuándo usarla", "Cuando el agente no importa: English is spoken worldwide.", False),
            ("Pasiva con modal", "The work must be done. The window can be opened.", False),
        ]),
        ("Phrasal verbs comunes", "Verbos multi-palabra.", [
            ("Ejemplos clave", "give up (rendirse), look up (buscar), turn off (apagar), put off (posponer).\nEj: I gave up smoking.", False),
            ("Más phrasals", "bring up (mencionar), run out of (quedarse sin), get along with (llevarse bien).\nEj: I ran out of money.", True),
        ]),
        ("Relativos", "Who, which, that, whose.", [
            ("Uso", "The man who called you is my brother. The book which is on the table is mine.\nThat para personas y cosas (inform.).", True),
        ]),
    ],
    "C1": [
        ("Inversión y énfasis", "Orden enfático.", [
            ("Never / Not only", "Never have I seen such a thing.\nNot only did he apologise, but he paid.", False),
            ("Cleft sentences", "It was yesterday that I saw him. What I need is time.", False),
        ]),
        ("Phrasal verbs avanzados", "Uso fino.", [
            ("Matices", "come across (encontrar por casualidad), brush up on (refrescar), rule out (descartar).", False),
            ("Más avanzados", "ward off (rechazar), fall back on (recurrir a), pin down (definir con precisión).", True),
        ]),
        ("Expresiones idiomáticas", "Coloquialismos.", [
            ("To break the ice", "Romper el hielo. Ej: He told a joke to break the ice.", False),
            ("Piece of cake", "Cosas muy fácil. Ej: The exam was a piece of cake.", False),
            ("To be over the moon", "Estar muy contento. Ej: She was over the moon with the news.", True),
        ]),
        ("Estilo indirecto", "Reported speech.", [
            ("Reglas", "He said (that) he was tired. 'I am' -> he was. 'will' -> would. 'today' -> that day.", True),
        ]),
    ],
    "C2": [
        ("Inglés académico", "Registro formal.", [
            ("Conectores", "Furthermore, nevertheless, thereby, albeit.\nEj: The results were clear; nevertheless, more research is needed.", True),
            ("Estructuras complejas", "Had I known, I would have helped. Rarely does one see such dedication.", True),
        ]),
        ("Matices y registro", "Tono y precisión.", [
            ("Sinónimos precisos", "big -> substantial / considerable. good -> commendable / exemplary.", True),
            ("Connotaciones", "thin (neutro) vs skinny (negativo) vs slim (positivo).", True),
        ]),
        ("Debate y argumentación", "Persuadir.", [
            ("Recursos", "It could be argued that..., One cannot overlook..., Admittedly,...\nEj: Admittedly, costs are high; however, benefits outweigh them.", True),
        ]),
    ],
}

for code, courses in content.items():
    lvl = level_objs[code]
    for i, (ctitle, cdesc, lessons) in enumerate(courses, start=1):
        course = Course(level_id=lvl.id, title=ctitle, description=cdesc, orden=i)
        db.add(course); db.flush()
        for j, (ltitle, lcontent, lprem) in enumerate(lessons, start=1):
            db.add(Lesson(course_id=course.id, title=ltitle, content=lcontent, orden=j, is_premium=lprem))

tests_data = {
    "A1": [("¿Cómo se dice 'yo soy'?", ["I am", "I is", "I are"], 0, "Primera persona: I am."),
           ("Pronombre para 'ella'", ["he", "she", "it"], 1, "She = ella."),
           ("'Cat' significa", ["perro", "gato", "pájaro"], 1, "Cat = gato.")],
    "A2": [("Pasado de 'go'", ["goed", "went", "gone"], 1, "Irregular: go -> went."),
           ("Futuro con plan", ["I will go", "I am going to go", "I go"], 1, "Going to para planes."),
           ("'Yesterday' usa", ["presente", "pasado", "futuro"], 1, "Yesterday -> pasado simple.")],
    "B1": [("Presente continuo de 'eat'", ["I eat", "I am eating", "I eaten"], 1, "am/is/are + -ing."),
           ("Comparativo de 'big'", ["biger", "bigger", "more big"], 1, "CVC -> doubling: bigger."),
           ("'Like' como estado", ["I am liking", "I like", "I liking"], 1, "Verbos de estado no usan -ing.")],
    "B2": [("Second conditional", ["If I go, I go", "If I went, I would go", "If I had gone"], 1, "Hipótesis presente: if + past, would."),
           ("Pasiva de 'write'", ["is write", "is written", "is writing"], 1, "be + participio."),
           ("Phrasal 'give up'", ["rendirse", "subir", "dar"], 0, "Give up = rendirse.")],
    "C1": [("Inversión con 'never'", ["Never I saw", "Never have I seen", "Never I have seen"], 1, "Inversión: Never + aux + suj + verb."),
           ("'Break the ice'", ["romper el hielo", "romper algo", "hacer hielo"], 0, "Romper el hielo socialmente."),
           ("'Brush up on'", ["olvidar", "refrescar", "pintar"], 1, "Brush up on = refrescar conocimiento.")],
    "C2": [("Conector formal", ["and then", "furthermore", "so"], 1, "Furthermore es formal."),
           ("Registro de 'big'", ["substantial", "huge", "large"], 0, "Substantial es preciso/formal."),
           ("'Albeit'", ["aunque", "pero", "porque"], 0, "Albeit = aunque.")],
}

for code, questions in tests_data.items():
    lvl = level_objs[code]
    test = Test(level_id=lvl.id, title=f"Test de Nivel {code}")
    db.add(test); db.flush()
    for prompt, options, correct, explanation in questions:
        db.add(Question(test_id=test.id, prompt=prompt, options=options, correct=correct, explanation=explanation))

db.commit()
print("Contenido ampliado cargado: 6 niveles, más lecciones por curso y tests por nivel.")
db.close()

# Completa a 20 preguntas por nivel (idempotente, solo agrega)
try:
    import migrate_questions
    migrate_questions.ensure_20_questions()
except Exception as e:
    print(f"AVISO al completar preguntas: {e}")
