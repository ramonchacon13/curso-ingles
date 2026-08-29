export const CATEGORIES = [
  {
    id: 'saludos',
    title: 'Saludos y presentaciones',
    img: 'friends',
    phrases: [
      { en: "Hi, I'm Alex. Nice to meet you.", es: "Hola, soy Alex. Encantado de conocerte." },
      { en: "What's your name?", es: "¿Cómo te llamas?" },
      { en: "I'm from Spain, but I live in Madrid.", es: "Soy de España, pero vivo en Madrid." },
      { en: "This is my friend Laura.", es: "Esta es mi amiga Laura." },
      { en: "How do you do?", es: "¿Cómo está usted?" },
      { en: "See you later!", es: "¡Hasta luego!" },
    ],
  },
  {
    id: 'cafe',
    title: 'En el café o restaurante',
    img: 'coffee',
    phrases: [
      { en: "A coffee and a croissant, please.", es: "Un café y un croissant, por favor." },
      { en: "Can I see the menu?", es: "¿Puedo ver el menú?" },
      { en: "I'd like the bill, please.", es: "Quisiera la cuenta, por favor." },
      { en: "Is this seat taken?", es: "¿Está ocupado este asiento?" },
      { en: "Could you bring me some water?", es: "¿Me trae un poco de agua?" },
      { en: "That was delicious, thank you.", es: "Estaba delicioso, gracias." },
    ],
  },
  {
    id: 'tienda',
    title: 'De compras',
    img: 'shopping',
    phrases: [
      { en: "How much does this cost?", es: "¿Cuánto cuesta esto?" },
      { en: "Do you have this in a larger size?", es: "¿Tienen esto en una talla más grande?" },
      { en: "I'm just looking, thanks.", es: "Solo estoy mirando, gracias." },
      { en: "Can I try it on?", es: "¿Puedo probármelo?" },
      { en: "Where are the changing rooms?", es: "¿Dónde están los probadores?" },
      { en: "I'll take it.", es: "Lo compro." },
    ],
  },
  {
    id: 'direcciones',
    title: 'Pedir direcciones',
    img: 'map',
    phrases: [
      { en: "Excuse me, where is the station?", es: "Disculpe, ¿dónde está la estación?" },
      { en: "How do I get to the museum?", es: "¿Cómo llego al museo?" },
      { en: "Go straight and turn left.", es: "Siga recto y gire a la izquierda." },
      { en: "Is it far from here?", es: "¿Está lejos de aquí?" },
      { en: "Can you show me on the map?", es: "¿Puede mostrármelo en el mapa?" },
      { en: "Thank you, you're very kind.", es: "Gracias, es usted muy amable." },
    ],
  },
  {
    id: 'emergencias',
    title: 'Ayuda y emergencias',
    img: 'ambulance',
    phrases: [
      { en: "Help! Call a doctor!", es: "¡Socorro! ¡Llame a un médico!" },
      { en: "I need a police officer.", es: "Necesito a un agente de policía." },
      { en: "Where is the nearest hospital?", es: "¿Dónde está el hospital más cercano?" },
      { en: "I lost my passport.", es: "Perdí mi pasaporte." },
      { en: "My phone is not working.", es: "Mi teléfono no funciona." },
      { en: "Please speak slowly.", es: "Por favor, hable despacio." },
    ],
  },
  {
    id: 'trabajo',
    title: 'Trabajo y estudios',
    img: 'laptop',
    phrases: [
      { en: "I have a meeting at three.", es: "Tengo una reunión a las tres." },
      { en: "Could you repeat that, please?", es: "¿Podría repetir eso, por favor?" },
      { en: "I'm learning English every day.", es: "Estudio inglés todos los días." },
      { en: "What do you do for a living?", es: "¿A qué se dedica usted?" },
      { en: "Let's schedule a call.", es: "Agendemos una llamada." },
      { en: "I'll send you an email.", es: "Le enviaré un correo." },
    ],
  },
]

export const STORY = {
  title: 'En el café',
  lines: [
    { speaker: 'Barista', en: "Hi! What can I get for you today?", es: "¡Hola! ¿Qué le sirvo hoy?", img: 'coffee' },
    { speaker: 'Tú', en: "A medium latte, please. To go.", es: "Un latte mediano, por favor. Para llevar.", img: 'coffee' },
    { speaker: 'Barista', en: "Sure! Anything to eat?", es: "¡Claro! ¿Algo para comer?", img: 'muffin' },
    { speaker: 'Tú', en: "A blueberry muffin sounds great.", es: "Un muffin de arándanos suena estupendo.", img: 'muffin' },
    { speaker: 'Barista', en: "That'll be four fifty. Cash or card?", es: "Son cuatro cincuenta. ¿Efectivo o tarjeta?", img: 'credit' },
    { speaker: 'Tú', en: "Card, thanks. Have a nice day!", es: "Tarjeta, gracias. ¡Que tenga un buen día!", img: 'friends' },
  ],
}
