import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
import models
from models import Level, Test, Question
from sqlalchemy import select


QUESTIONS_BANK = {
    "A1": [
        ("¿Cómo se dice 'yo soy'?", ["I am", "I is", "I are"], 0, "Primera persona: I am."),
        ("Pronombre para 'ella'", ["he", "she", "it"], 1, "She = ella."),
        ("'Cat' significa", ["perro", "gato", "pájaro"], 1, "Cat = gato."),
        ("¿Cómo se dice 'gracias' en inglés?", ["thank you", "sorry", "please"], 0, "Thank you = gracias."),
        ("El pronombre 'we' significa...", ["yo", "nosotros", "ellos"], 1, "We = nosotros."),
        ("¿Qué significa 'book'?", ["libro", "mesa", "coche"], 0, "Book = libro."),
        ("Forma negativa de 'I am':", ["I am not", "I not am", "not I am"], 0, "Negativo: I am not."),
        ("¿Cómo se dice 'buenos días'?", ["good night", "good morning", "good bye"], 1, "Good morning = buenos días."),
        ("'He' se refiere a...", ["ella", "él", "ello"], 1, "He = él."),
        ("¿Cuál es el plural de 'cat'?", ["cats", "caties", "cates"], 0, "Plural regular: cats."),
        ("¿Cómo se dice 'tengo un perro'?", ["I have a dog", "I has a dog", "I am a dog"], 0, "Have = tener (I have)."),
        ("'Water' significa...", ["fuego", "agua", "viento"], 1, "Water = agua."),
        ("¿Qué artículo usas antes de una vocal?", ["a", "an", "the"], 1, "An antes de vocal (an apple)."),
        ("¿Cómo preguntas '¿Cómo te llamas?'?", ["What is your name?", "Where is your name?", "Who is your name?"], 0, "What is your name? = ¿Cómo te llamas?"),
        ("'Yes' significa...", ["no", "sí", "quizás"], 1, "Yes = sí."),
        ("Forma del verbo 'to be' para 'they':", ["they is", "they are", "they am"], 1, "They + are."),
        ("¿Cómo se dice 'adiós'?", ["hello", "goodbye", "thanks"], 1, "Goodbye = adiós."),
        ("'Apple' es...", ["una fruta", "un animal", "un color"], 0, "Apple = manzana (fruta)."),
        ("¿Qué significa 'friend'?", ["amigo", "familia", "profesor"], 0, "Friend = amigo."),
        ("¿Cómo se dice 'no entiendo'?", ["I don't understand", "I not understand", "I no understand"], 0, "Don't understand = no entiendo."),
    ],
    "A2": [
        ("Pasado de 'go'", ["goed", "went", "gone"], 1, "Irregular: go -> went."),
        ("Futuro con plan", ["I will go", "I am going to go", "I go"], 1, "Going to para planes."),
        ("'Yesterday' usa", ["presente", "pasado", "futuro"], 1, "Yesterday -> pasado simple."),
        ("Pasado de 'eat'", ["eated", "ate", "eaten"], 1, "Irregular: eat -> ate."),
        ("'She ___ to the park yesterday.'", ["go", "went", "goes"], 1, "Pasado: went."),
        ("¿Cómo se dice 'la semana pasada'?", ["last week", "next week", "this week"], 0, "Last week = la semana pasada."),
        ("Futuro con 'will': 'I ___ help you.'", ["will", "going", "am"], 0, "Will + verbo base."),
        ("'There ___ a book on the table.'", ["is", "are", "am"], 0, "There is (singular)."),
        ("¿Qué significa 'under'?", ["sobre", "debajo de", "al lado de"], 1, "Under = debajo de."),
        ("Comparativo de 'small':", ["smaller", "more small", "smalest"], 0, "Corto + -er: smaller."),
        ("'Often' es un adverbio de...", ["frecuencia", "lugar", "tiempo futuro"], 0, "Often = a menudo (frecuencia)."),
        ("Pasado de 'see'", ["saw", "seen", "seeed"], 0, "Irregular: see -> saw."),
        ("'I am going to ___ TV.'", ["watch", "watching", "watched"], 0, "Going to + base: watch."),
        ("¿Cómo se dice 'cerca de'?", ["next to", "far from", "under"], 0, "Next to = al lado/cerca de."),
        ("'They ___ football every Sunday.'", ["plays", "play", "playing"], 1, "Plural: play."),
        ("¿Qué significa 'expensive'?", ["barato", "caro", "gratis"], 1, "Expensive = caro."),
        ("Pasado negativo: 'I ___ like it.'", ["didn't", "don't", "doesn't"], 0, "Pasado con didn't."),
        ("'In' se usa para...", ["meses y años", "un momento concreto", "nada"], 0, "In + meses/años (in July)."),
        ("¿Cómo se dice '¿Qué hiciste?'?", ["What do you do?", "What did you do?", "What are you doing?"], 1, "Did para pasado."),
        ("'Happy' es...", ["triste", "feliz", "grande"], 1, "Happy = feliz."),
    ],
    "B1": [
        ("Presente continuo de 'eat'", ["I eat", "I am eating", "I eaten"], 1, "am/is/are + -ing."),
        ("Comparativo de 'big'", ["biger", "bigger", "more big"], 1, "CVC -> doubling: bigger."),
        ("'Like' como estado", ["I am liking", "I like", "I liking"], 1, "Verbos de estado no usan -ing."),
        ("Pasado continuo: 'I ___ when you called.'", ["was eating", "ate", "eat"], 0, "Was/were + -ing."),
        ("Comparativo de 'good':", ["gooder", "better", "best"], 1, "Irregular: good -> better."),
        ("'There ___ some water in the glass.'", ["is", "are", "be"], 0, "Water es incontable? No, incontable en cantidad -> is."),
        ("'I have never ___ to London.'", ["went", "gone", "been"], 2, "Been (estado). Have been."),
        ("Superlativo de 'big':", ["bigest", "biggest", "most big"], 1, "CVC dobla: biggest."),
        ("'She's interested ___ music.'", ["on", "in", "at"], 1, "Interested in."),
        ("¿Cómo se dice 'solía jugar'?", ["I used to play", "I use to play", "I using to play"], 0, "Used to = hábito pasado."),
        ("'Must' indica...", ["obligación fuerte", "posibilidad", "prohibición"], 0, "Must = deber/obligación."),
        ("Presente perfecto: 'I ___ finished.'", ["has", "have", "am"], 1, "I have."),
        ("'While' introduce...", ["una acción en progreso", "una decisión", "nada"], 0, "While = mientras (progreso)."),
        ("¿Qué significa 'however'?", ["porque", "sin embargo", "también"], 1, "However = sin embargo."),
        ("'He suggested ___ early.'", ["to leave", "leaving", "leave"], 1, "Suggest + -ing."),
        ("Pasado de 'buy'", ["bought", "buyed", "bring"], 0, "Irregular: buy -> bought."),
        ("'Much' se usa con...", ["contables", "incontables", "ambos"], 1, "Much + incontable."),
        ("¿Cómo se dice 'ya lo he visto'?", ["I already saw it", "I have already seen it", "I see it already"], 1, "Presente perfecto."),
        ("'Although' significa...", ["aunque", "pero", "y"], 0, "Although = aunque."),
        ("Third person de 'study':", ["studys", "studies", "studyies"], 1, "Consonante + y -> ies."),
    ],
    "B2": [
        ("Second conditional", ["If I go, I go", "If I went, I would go", "If I had gone"], 1, "Hipótesis presente: if + past, would."),
        ("Pasiva de 'write'", ["is write", "is written", "is writing"], 1, "be + participio."),
        ("Phrasal 'give up'", ["rendirse", "subir", "dar"], 0, "Give up = rendirse."),
        ("Pasiva: 'The window ___ opened.'", ["is", "are", "be"], 0, "The window (singular) -> is opened."),
        ("Zero conditional: 'If you heat ice, it ___'", ["melts", "melt", "melted"], 0, "Zero: presente + presente."),
        ("Phrasal 'look up':", ["mirar arriba", "buscar (en diccionario)", "cuidar"], 1, "Look up = buscar."),
        ("Relativo para personas:", ["which", "who", "whose"], 1, "Who para personas."),
        ("Mixed conditional: 'If I ___ rich, I would travel.'", ["am", "were", "be"], 1, "Second: were."),
        ("Pasiva con modal: 'The work ___ done.'", ["must be", "must is", "must are"], 0, "Must + be + participio."),
        ("Phrasal 'turn off':", ["encender", "apagar", "subir"], 1, "Turn off = apagar."),
        ("'That' en cláusulas de relativo es para...", ["solo personas", "personas y cosas (inform.)", "solo tiempo"], 1, "That: personas y cosas."),
        ("Third conditional: 'If she ___ studied, she would have passed.'", ["has", "had", "have"], 1, "Third: past perfect (had studied)."),
        ("¿Cómo se dice 'fue escrito por'?", ["was written by", "is write by", "wrote by"], 0, "Pasiva pasado: was written by."),
        ("Phrasal 'put off':", ["hacer", "posponer", "poner"], 1, "Put off = posponer."),
        ("'Whose' se usa para...", ["posesión", "lugar", "tiempo"], 0, "Whose = de quién (posesión)."),
        ("Pasiva: 'English ___ worldwide.'", ["is spoken", "speaks", "is speak"], 0, "Inglés se habla."),
        ("Phrasal 'run out of':", ["quedarse sin", "correr", "salir"], 0, "Run out of = quedarse sin."),
        ("First conditional: 'If it rains, I ___ stay.'", ["will", "would", "am"], 0, "First: will."),
        ("'Which' se refiere a...", ["personas", "cosas", "tiempo"], 1, "Which para cosas."),
        ("Phrasal 'get along with':", ["llevarse bien con", "obtener", "irse"], 0, "Get along with = llevarse bien."),
    ],
    "C1": [
        ("Inversión con 'never'", ["Never I saw", "Never have I seen", "Never I have seen"], 1, "Inversión: Never + aux + suj + verb."),
        ("'Break the ice'", ["romper el hielo", "romper algo", "hacer hielo"], 0, "Romper el hielo socialmente."),
        ("'Brush up on'", ["olvidar", "refrescar", "pintar"], 1, "Brush up on = refrescar conocimiento."),
        ("Inversión con 'not only':", ["Not only he came, but...", "Not only did he come, but...", "Not only he did come, but..."], 1, "Inversión: Not only + aux + suj."),
        ("Cleft: 'It was yesterday ___ I saw him.'", ["when", "that", "which"], 1, "Cleft con that."),
        ("'Come across' significa...", ["encontrar por casualidad", "venir", "cruzar"], 0, "Come across = encontrar por azar."),
        ("Reported speech: 'I am tired' -> He said he ___", ["is", "was", "were"], 1, "Presente -> pasado."),
        ("'Rule out' significa...", ["descartar", "gobernar", "salir"], 0, "Rule out = descartar."),
        ("Inversión con 'rarely':", ["Rarely he goes", "Rarely does he go", "Rarely he does go"], 1, "Rarely + aux + suj."),
        ("'Ward off' significa...", ["rechazar", "guardar", "irse"], 0, "Ward off = rechazar/evitar."),
        ("Reported: 'will' se convierte en...", ["would", "will", "won't"], 0, "Will -> would."),
        ("'To be over the moon' significa...", ["estar enfadado", "estar muy contento", "estar en la luna"], 1, "Over the moon = muy feliz."),
        ("Cleft: 'What I need ___ time.'", ["is", "are", "be"], 0, "What I need (singular) -> is."),
        ("'Fall back on' significa...", ["recurrir a", "caer", "apoyar"], 0, "Fall back on = recurrir a."),
        ("Reported: 'today' se convierte en...", ["today", "that day", "tomorrow"], 1, "Today -> that day."),
        ("'Pin down' significa...", ["definir con precisión", "clavar", "bajar"], 0, "Pin down = precisar."),
        ("Reported: 'yesterday' se convierte en...", ["yesterday", "the day before", "tomorrow"], 1, "Yesterday -> the day before."),
        ("'Piece of cake' significa...", ["algo difícil", "algo muy fácil", "un pastel"], 1, "Piece of cake = muy fácil."),
        ("Reported: 'I go' -> He said he ___", ["goes", "went", "go"], 1, "Presente -> pasado."),
        ("'Brush up on' se usa para...", ["refrescar conocimiento", "pintar", "olvidar"], 0, "Brush up on = refrescar."),
    ],
    "C2": [
        ("Conector formal", ["and then", "furthermore", "so"], 1, "Furthermore es formal."),
        ("Registro de 'big'", ["substantial", "huge", "large"], 0, "Substantial es preciso/formal."),
        ("'Albeit'", ["aunque", "pero", "porque"], 0, "Albeit = aunque."),
        ("Conector 'nevertheless' significa...", ["por tanto", "sin embargo", "adicionalmente"], 1, "Nevertheless = sin embargo."),
        ("Registro de 'huge':", ["muy formal", "menos formal", "técnico"], 1, "Huge = menos formal que substantial."),
        ("'Thin' vs 'slim': 'slim' es...", ["negativo", "positivo", "neutro"], 1, "Slim = positivo."),
        ("Conector 'furthermore' es...", ["formal", "coloquial", "raro"], 0, "Furthermore = formal."),
        ("'Skinny' suele ser...", ["positivo", "negativo", "neutro"], 1, "Skinny = negativo."),
        ("Recurso de debate 'It could be argued that...' sirve para...", ["persuadir", "saludar", "despedir"], 0, "Argumentar/persuadir."),
        ("Conector 'thereby' indica...", ["resultado", "oposición", "tiempo"], 0, "Thereby = por lo cual (resultado)."),
        ("'Commendable' es sinónimo preciso de...", ["good", "bad", "big"], 0, "Commendable = bueno (preciso)."),
        ("Inversión: 'Had I known, I ___ helped.'", ["would have", "will have", "would"], 0, "Mixed: would have + participio."),
        ("'Exemplary' es...", ["malo", "ejemplar/excelente", "grande"], 1, "Exemplary = ejemplar."),
        ("Connotación de 'considerable':", ["pequeño", "notable/grande", "negativo"], 1, "Considerable = notable."),
        ("Registro de 'substantial evidence':", ["coloquial", "académico/formal", "vulgar"], 1, "Substantial = académico."),
        ("'Thin' vs 'slim': 'thin' es...", ["positivo", "neutro", "negativo"], 1, "Thin = neutro."),
        ("Conector 'albeit' va con...", ["solo verbos", "frase nominal o adjetivo", "solo sustantivos"], 1, "Albeit + frase nominal/adjetivo."),
        ("'Admittedly' se usa para...", ["conceder un punto", "negar", "preguntar"], 0, "Admittedly = se admite."),
        ("Debate: 'One cannot overlook...' significa...", ["no se puede ignorar", "se puede ver", "olvidar"], 0, "Overlook = pasar por alto."),
        ("Registro de 'large' frente a 'substantial':", ["large es más formal", "son iguales", "substantial es más preciso"], 2, "Substantial aporta precisión/registro."),
    ],
}


def ensure_20_questions():
    db = SessionLocal()
    try:
        for code, bank in QUESTIONS_BANK.items():
            level = db.scalar(select(Level).where(Level.code == code))
            if not level:
                continue
            tests = db.scalars(select(Test).where(Test.level_id == level.id)).all()

            # Reusar un test existente como "Parte 1" (preserva resultados de usuarios)
            # y crear "Parte 2". Así no borramos registros.
            test1 = next((t for t in tests if "Parte 1" in t.title), None)
            test2 = next((t for t in tests if "Parte 2" in t.title), None)
            if test1 is None:
                if tests:
                    test1 = tests[0]
                    test1.title = f"Test de Nivel {code} - Parte 1"
                else:
                    test1 = Test(level_id=level.id, title=f"Test de Nivel {code} - Parte 1")
                    db.add(test1)
                db.flush()
            if test2 is None:
                test2 = Test(level_id=level.id, title=f"Test de Nivel {code} - Parte 2")
                db.add(test2)
                db.flush()

            # Mapa prompt -> Question ya existente en este nivel
            existing = {}
            for t in tests:
                for q in db.scalars(select(Question).where(Question.test_id == t.id)).all():
                    existing[q.prompt] = q

            for idx, (prompt, options, correct, explanation) in enumerate(bank):
                target = test1 if idx < 10 else test2
                if prompt in existing:
                    q = existing[prompt]
                    if q.test_id != target.id:
                        q.test_id = target.id  # mover de test (no borra resultados)
                else:
                    q = Question(
                        test_id=target.id,
                        prompt=prompt,
                        options=options,
                        correct=correct,
                        explanation=explanation,
                    )
                    db.add(q)
                    existing[prompt] = q
        db.commit()
        print("ensure_20_questions: 2 tests x 10 preguntas por nivel listos.")
    except Exception as e:
        db.rollback()
        print(f"AVISO ensure_20_questions: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    ensure_20_questions()
