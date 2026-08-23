import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
import models
from models import Level, Test, Question, TestResult
from sqlalchemy import select, func


# Objetivo por nivel (múltiplo de 10; se reparte en tests de 10).
# A1=20, A2=30, B1=40, B2=50, C1=50, C2=50  ->  2/3/4/5/5/5 tests por nivel.
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
        ("'She has ___ hair.'", ["long", "length", "longly"], 0, "Long = largo (adjetivo)."),
        ("¿Cómo se dice 'tengo 25 años'?", ["I have 25 years", "I am 25 years old", "I am 25 years"], 1, "I am 25 years old."),
        ("'They went ___ the store.'", ["to", "at", "in"], 0, "To + lugar."),
        ("Pasado de 'have':", ["has", "had", "haved"], 1, "Irregular: have -> had."),
        ("'We ___ TV every night.'", ["watch", "watches", "watching"], 0, "Plural: watch."),
        ("¿Qué significa 'behind'?", ["delante de", "detrás de", "encima de"], 1, "Behind = detrás de."),
        ("Comparativo de 'easy':", ["easier", "more easy", "easyer"], 0, "Y consonante -> easier."),
        ("'I didn't ___ to the party.'", ["went", "go", "gone"], 1, "Tras didn't va verbo base."),
        ("'There are ___ apples on the tree.'", ["is", "are", "am"], 1, "Plural -> are."),
        ("¿Cómo se dice 'me gusta el café'?", ["I like coffee", "I like the coffee", "I am liking coffee"], 0, "I like coffee."),
    ],
    "B1": [
        ("Presente continuo de 'eat'", ["I eat", "I am eating", "I eaten"], 1, "am/is/are + -ing."),
        ("Comparativo de 'big'", ["biger", "bigger", "more big"], 1, "CVC -> doubling: bigger."),
        ("'Like' como estado", ["I am liking", "I like", "I liking"], 1, "Verbos de estado no usan -ing."),
        ("Pasado continuo: 'I ___ when you called.'", ["was eating", "ate", "eat"], 0, "Was/were + -ing."),
        ("Comparativo de 'good':", ["gooder", "better", "best"], 1, "Irregular: good -> better."),
        ("'There ___ some water in the glass.'", ["is", "are", "be"], 0, "Water es incontable -> is."),
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
        ("'I have lived here ___ 2010.'", ["for", "since", "from"], 1, "Since + punto en el tiempo."),
        ("Pasado de 'run':", ["ran", "runned", "run"], 0, "Irregular: run -> ran."),
        ("'She ___ to the doctor yesterday.'", ["goes", "went", "gone"], 1, "Pasado: went."),
        ("Presente perfecto negativo: 'I ___ finished.'", ["haven't", "hasn't", "don't"], 0, "I haven't."),
        ("'He's good ___ math.'", ["on", "at", "in"], 1, "Good at."),
        ("Comparativo de 'bad':", ["bader", "worse", "worst"], 1, "Irregular: bad -> worse."),
        ("'We use ___ for uncountable nouns.'", ["much", "many", "a"], 1, "Much con incontable."),
        ("'If I ___ you, I would go.'", ["was", "were", "am"], 1, "Second conditional: were."),
        ("¿Cómo se dice 'ya he comido'?", ["I already ate", "I have already eaten", "I ate already"], 1, "Presente perfecto."),
        ("'They are interested ___ the project.'", ["on", "in", "at"], 1, "Interested in."),
        ("Pasado de 'write':", ["wrote", "written", "writed"], 0, "Irregular: write -> wrote."),
        ("'Can you ___ me?'", ["help", "helps", "helping"], 0, "Can + base."),
        ("'She has ___ to Paris twice.'", ["went", "been", "go"], 1, "Been (estado)."),
        ("'I'm used ___ early.'", ["to get up", "to getting up", "get up"], 1, "Used to + -ing."),
        ("Superlativo de 'good':", ["goodest", "best", "better"], 1, "Irregular: good -> best."),
        ("'He suggested ___ to the cinema.'", ["to go", "going", "go"], 1, "Suggest + -ing."),
        ("'There isn't ___ milk.'", ["some", "any", "many"], 1, "Any en negativas."),
        ("Pasado de 'teach':", ["taught", "teached", "teached"], 0, "Irregular: teach -> taught."),
        ("'I have ___ finished my homework.'", ["yet", "already", "still"], 1, "Already en positivas."),
        ("'We ___ playing when it started to rain.'", ["were", "are", "was"], 0, "Plural: were."),
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
        ("'If he ___ here, he would help.'", ["was", "were", "is"], 1, "Second: were."),
        ("Pasiva: 'The book ___ by him.'", ["was written", "wrote", "was wrote"], 0, "Was + participio."),
        ("'I'm looking forward ___ you.'", ["to see", "to seeing", "see"], 1, "Look forward to + -ing."),
        ("Phrasal 'take off':", ["despegar", "ponerse", "llevar"], 0, "Take off = despegar."),
        ("'The report ___ tomorrow.'", ["will be finished", "will finish", "is finish"], 0, "Pasiva futura."),
        ("Relativo para cosas:", ["who", "which", "whom"], 1, "Which para cosas."),
        ("'Despite ___ tired, he worked.'", ["being", "be", "was"], 0, "Despite + -ing."),
        ("Phrasal 'come up with':", ["inventar", "subir", "venir"], 0, "Come up with = idear."),
        ("'He asked me where I ___ from.'", ["came", "come", "was coming"], 1, "Reported: come (invariable)."),
        ("Third conditional: 'If we ___ earlier, we would have caught it.'", ["had left", "left", "leave"], 0, "Past perfect."),
        ("'The window was broken ___ the wind.'", ["by", "with", "from"], 0, "By + agente."),
        ("Phrasal 'set up':", ["establecer", "sentar", "poner"], 0, "Set up = establecer/montar."),
        ("'It's high time we ___ home.'", ["go", "went", "gone"], 1, "Subjuntivo pasado: went."),
        ("Pasiva con 'can': 'This ___ done.'", ["can be", "can is", "can are"], 0, "Can + be + participio."),
        ("'Whom' se usa para...", ["sujeto", "objeto", "posesión"], 1, "Whom = objeto."),
        ("Phrasal 'break down':", ["romperse", "quebrar", "bajar"], 0, "Break down = averiarse."),
        ("'I wish I ___ richer.'", ["was", "were", "am"], 1, "Wish + were."),
        ("'The cake ___ by my mother.'", ["is made", "made", "is make"], 0, "Pasiva presente."),
        ("Phrasal 'get over':", ["superar", "obtener", "llegar"], 0, "Get over = superar."),
        ("'He is the man ___ won the prize.'", ["which", "who", "whose"], 1, "Who para personas."),
        ("Cleft: 'It was in June ___ I met her.'", ["when", "that", "which"], 1, "Cleft con that."),
        ("'The documents ___ yet.'", ["haven't signed", "haven't been signed", "weren't signed"], 1, "Pasiva perfecta."),
        ("Phrasal 'look after':", ["cuidar", "buscar", "mirar"], 0, "Look after = cuidar."),
        ("'If it ___ sunny, we would go.'", ["was", "were", "is"], 1, "Second: were."),
        ("'The letter ___ by the postman.'", ["was delivered", "delivered", "was deliver"], 0, "Pasiva pasado."),
        ("Phrasal 'put up with':", ["tolerar", "poner", "subir"], 0, "Put up with = tolerar."),
        ("'She suggested that he ___ earlier.'", ["leaves", "left", "leave"], 1, "Subjuntivo: leave."),
        ("Pasiva: 'English ___ in many countries.'", ["is spoken", "speaks", "is speak"], 0, "Inglés se habla."),
        ("'I'd rather you ___ now.'", ["go", "went", "gone"], 1, "Would rather + pasado."),
        ("Phrasal 'run into':", ["encontrarse con", "correr", "entrar"], 0, "Run into = encontrarse con."),
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
        ("'Hardly ___ when it started raining.'", ["I arrived", "had I arrived", "I had arrived"], 1, "Inversión: Hardly + aux + suj."),
        ("'Not until' invierte: 'Not until midnight ___.'", ["he arrived", "did he arrive", "he did arrive"], 1, "Inversión con not until."),
        ("'Scarcely ___ the door when...'", ["I opened", "had I opened", "I had opened"], 1, "Scarcely + aux + suj."),
        ("'It was the teacher ___ helped me.'", ["who", "which", "what"], 0, "Cleft con who."),
        ("'Bring up' (un tema) significa...", ["mencionar", "subir", "traer"], 0, "Bring up = sacar a colación."),
        ("'Get across' significa...", ["comunicar", "cruzar", "obtener"], 0, "Get across = hacer entender."),
        ("Reported: 'I can' -> He said he ___", ["can", "could", "cans"], 1, "Can -> could."),
        ("'On no account' invierte: 'On no account ___'", ["we complain", "do we complain", "we do complain"], 1, "Inversión: On no account + aux + suj."),
        ("'It's high time' va con...", ["presente", "pasado", "futuro"], 1, "Subjuntivo pasado."),
        ("'Put up with' significa...", ["tolerar", "poner", "subir"], 0, "Put up with = tolerar."),
        ("'Were I you, I ___ go.'", ["will", "would", "shall"], 1, "Inversión condicional: would."),
        ("'The more you read, ___ you know.'", ["the more", "more", "the most"], 0, "The + comparativo... the + comparativo."),
        ("'Hardly ever' significa...", ["casi siempre", "casi nunca", "a veces"], 1, "Hardly ever = casi nunca."),
        ("'Set out' significa...", ["salir", "poner", "establecer"], 0, "Set out = ponerse en marcha."),
        ("Reported: 'must' -> He said he ___", ["must", "had to", "musted"], 1, "Must -> had to."),
        ("'Little did he ___ about it.'", ["know", "knew", "known"], 0, "Little + aux + suj + verbo base."),
        ("'Account for' significa...", ["explicar", "contar", "acunar"], 0, "Account for = explicar."),
        ("'It was yesterday ___ I called.'", ["when", "that", "which"], 1, "Cleft con that."),
        ("'Make up' (una historia) significa...", ["inventar", "maquillar", "hacer"], 0, "Make up = inventar."),
        ("'Rarely' invierte: 'Rarely ___ he late.'", ["is", "was", "were"], 1, "Rarely + aux + suj."),
        ("'By no means' invierte: 'By no means ___'", ["it is easy", "is it easy", "it easy is"], 1, "Inversión: By no means + aux + suj."),
        ("Reported: 'these' -> He said ___", ["these", "those", "that"], 1, "These -> those."),
        ("'Stand for' significa...", ["representar", "estar", "pararse"], 0, "Stand for = representar."),
        ("'Only then' invierte: 'Only then ___'", ["I left", "did I leave", "I did leave"], 1, "Inversión: Only then + aux + suj."),
        ("'Carry out' significa...", ["realizar", "llevar", "transportar"], 0, "Carry out = llevar a cabo."),
        ("'He is said ___ a genius.'", ["to be", "be", "being"], 0, "He is said to be."),
        ("'It was not until...' usa...", ["inversión", "presente", "ninguna"], 0, "Inversión tras not until."),
        ("'Come into' significa...", ["heredar", "entrar", "venir"], 0, "Come into = heredar (dinero)."),
        ("'Were they to ask, I ___ help.'", ["will", "would", "shan't"], 1, "Inversión were + suj + to."),
        ("'Take on' significa...", ["asumir", "tomar", "llevar"], 0, "Take on = asumir (responsabilidad)."),
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
        ("'Notwithstanding' significa...", ["a pesar de", "debido a", "sin"], 0, "Notwithstanding = a pesar de."),
        ("'Arguably' se usa para...", ["discutir un punto", "afirmar con matiz", "negar"], 1, "Arguably = se podría argumentar."),
        ("'The former... the latter' se refiere a...", ["dos elementos", "tres", "uno"], 0, "Former/latter para dos."),
        ("'Insofar as' significa...", ["en la medida en que", "aunque", "porque"], 0, "Insofar as = en la medida en que."),
        ("'Per se' significa...", ["por sí mismo", "personalmente", "periódicamente"], 0, "Per se = por sí mismo."),
        ("'To all intents and purposes' significa...", ["en efecto", "a propósito", "intencionalmente"], 0, "En efecto/prácticamente."),
        ("'Mitigate' significa...", ["agravar", "mitigar", "mediar"], 1, "Mitigate = mitigar."),
        ("'Aforementioned' se refiere a...", ["mencionado antes", "futuro", "desconocido"], 0, "Aforementioned = ya mencionado."),
        ("'Nevertheless' es un conector de...", ["oposición", "adición", "causa"], 0, "Nevertheless = oposición."),
        ("'Concur' significa...", ["discrepar", "coincidir", "correr"], 1, "Concur = coincidir."),
        ("'To preclude' significa...", ["incluir", "excluir/impedir", "prever"], 1, "Preclude = impedir."),
        ("'Albeit' + frase...", ["nominal/adj", "solo verbo", "solo sujeto"], 0, "Albeit + frase nominal/adjetivo."),
        ("'Inherent' significa...", ["inerente", "heredado", "interno"], 0, "Inherent = inherente."),
        ("'To underscore' significa...", ["subrayar/enfatizar", "restar", "bajar"], 0, "Underscore = subrayar."),
        ("'Not least' significa...", ["no menos", "especialmente", "nada menos"], 1, "Not least = especialmente."),
        ("'To posit' significa...", ["suponer", "poner", "posar"], 0, "Posit = postular."),
        ("'Allegedly' se traduce como...", ["supuestamente", "indudablemente", "legalmente"], 0, "Allegedly = supuestamente."),
        ("'To the extent that' significa...", ["en la medida en que", "aunque", "tanto que"], 0, "En la medida en que."),
        ("'Pivotal' significa...", ["secundario", "pivotal/clave", "pasivo"], 1, "Pivotal = clave."),
        ("'To delineate' significa...", ["borrar", "delinear/describir", "retirar"], 1, "Delineate = delinear."),
        ("'By the same token' significa...", ["del mismo modo", "por el mismo token", "sin embargo"], 0, "Del mismo modo."),
        ("'To obfuscate' significa...", ["aclarar", "confundir/oscurecer", "obstruir"], 1, "Obfuscate = ofuscar."),
        ("'Salient' significa...", ["saliente/prominente", "saliendo", "salado"], 0, "Salient = prominente."),
        ("'To extrapolate' significa...", ["interpolar", "extrapolar", "extraer"], 1, "Extrapolate = extrapolar."),
        ("'Incontrovertible' significa...", ["discutible", "incuestionable", "controvertido"], 1, "Incontrovertible = incuestionable."),
        ("'To eschew' significa...", ["evitar", "abrazar", "esconder"], 0, "Eschew = evitar."),
        ("'Quintessential' significa...", ["cuestionable", "quintal", "quintasencial/arquetípico"], 2, "Quintessential = arquetípico."),
        ("'To brook no delay' significa...", ["no tolerar", "gestionar", "buscar"], 0, "Brook = tolerar (negativo)."),
        ("'Loathe' significa...", ["amar", "detestar", "flotar"], 1, "Loathe = detestar."),
        ("'To gainsay' significa...", ["confirmar", "contradecir", "ganar"], 1, "Gainsay = contradecir."),
    ],
}


def ensure_20_questions():
    db = SessionLocal()
    try:
        for code, bank in QUESTIONS_BANK.items():
            level = db.scalar(select(Level).where(Level.code == code))
            if not level:
                continue
            total = len(bank)
            k = total // 10  # cantidad de tests de 10
            tests = db.scalars(select(Test).where(Test.level_id == level.id)).all()

            # Reusar tests existentes (conserva resultados) y crear los que falten
            target_tests = []
            for i in range(k):
                if i < len(tests):
                    t = tests[i]
                    t.title = f"Test de Nivel {code} - Parte {i + 1}"
                else:
                    t = Test(level_id=level.id, title=f"Test de Nivel {code} - Parte {i + 1}")
                    db.add(t)
                target_tests.append(t)
            db.flush()

            # Mapa prompt -> Question ya existente en este nivel
            existing = {}
            for t in tests:
                for q in db.scalars(select(Question).where(Question.test_id == t.id)).all():
                    existing[q.prompt] = q

            for idx, (prompt, options, correct, explanation) in enumerate(bank):
                target = target_tests[idx // 10]
                if prompt in existing:
                    q = existing[prompt]
                    if q.test_id != target.id:
                        q.test_id = target.id  # mover (no borra resultados)
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

            # Limpiar tests sobrantes sin preguntas ni resultados
            for t in tests:
                if t not in target_tests:
                    has_q = db.scalar(select(func.count(Question.id)).where(Question.test_id == t.id))
                    has_r = db.scalar(select(func.count(TestResult.id)).where(TestResult.test_id == t.id))
                    if (has_q or 0) == 0 and (has_r or 0) == 0:
                        db.delete(t)
        db.commit()
        print("ensure_20_questions: tests por nivel completados (20/30/40/50/50/50).")
    except Exception as e:
        db.rollback()
        print(f"AVISO ensure_20_questions: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    ensure_20_questions()
