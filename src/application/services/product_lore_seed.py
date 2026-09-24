"""
Servicio maestro de sembrado de Grimorio Lore por Ítem para Masters of the Universe Origins.
Contiene biografías canónicas en español, citas de reverso de blíster (cardbacks Mattel)
y extractos de wiki oficiales.
REGLA ESTRICTA: Aplica única y exclusivamente a la línea Origins (is_vintage == False).
"""

from typing import Dict, Any, Optional
from loguru import logger
from sqlalchemy.orm import Session
from src.domain.models import ProductModel, ProductLoreModel, CharacterLoreModel
from src.domain.motu_canon_database import resolve_motu_profile

# Biografías canónicas de reverso de blíster (Cardback Bios) y frases oficiales de Mattel en español
CARDBACK_BIOS_ORIGINS: Dict[str, Dict[str, str]] = {
    # ── HE-MAN & VARIANTES ──
    "he-man": {
        "subtitle": "El Hombre Más Poderoso del Universo",
        "quote": "¡Por el poder de Grayskull... Yo tengo el poder!",
        "flavor_quote_author": "He-Man",
        "special_move": "Por el Poder de Grayskull",
        "lore": "Defensor jurado de los secretos de Castle Grayskull y de toda Eternia frente a las fuerzas del mal. Portador de la legendaria Espada del Poder.",
        "source_url": "https://he-man.fandom.com/wiki/He-Man"
    },
    "battle armor he-man": {
        "subtitle": "Campeón Acorazado de Grayskull",
        "quote": "¡Ningún ataque atravesará la coraza forjada para la batalla!",
        "flavor_quote_author": "He-Man",
        "special_move": "Impacto Sísmico de Coraza",
        "lore": "Equipado con una armadura mística indestructible que absorbe los golpes más devastadores de Skeletor. La última línea de defensa en el combate cuerpo a cuerpo.",
        "source_url": "https://he-man.fandom.com/wiki/Battle_Armor_He-Man"
    },
    "flying fists he-man": {
        "subtitle": "Guerrero de los Puños Voladores",
        "quote": "¡Mis puños giran con la furia de una tormenta cósmica!",
        "flavor_quote_author": "He-Man",
        "special_move": "Torbellino de Puños Giratorios",
        "lore": "Con su armadura voladora y su maza giratoria de doble filo, He-Man golpea a los esbirros del mal en un torbellino imparable de fuerza.",
        "source_url": "https://he-man.fandom.com/wiki/Flying_Fists_He-Man"
    },
    "thunder punch he-man": {
        "subtitle": "Titán del Trueno",
        "quote": "¡Siente la conmoción del trueno de Eternia!",
        "flavor_quote_author": "He-Man",
        "special_move": "Golpe del Trueno Devastador",
        "lore": "Canalizando energía de relámpago puro en su mochila explosiva, cada impacto de su puño detona con la fuerza atronadora de un cataclismo.",
        "source_url": "https://he-man.fandom.com/wiki/Thunder_Punch_He-Man"
    },
    "laser power he-man": {
        "subtitle": "Guerrero de Luz Fotónica",
        "quote": "¡La luz de Grayskull disipará todas las sombras!",
        "flavor_quote_author": "He-Man",
        "special_move": "Haz Láser Concentrado",
        "lore": "Armado con una espada translúcida alimentada por energía fotónica pura, diseñada para atravesar las tinieblas más densas de Snake Mountain.",
        "source_url": "https://he-man.fandom.com/wiki/Laser_Power_He-Man"
    },

    # ── SKELETOR & VARIANTES ──
    "skeletor": {
        "subtitle": "Señor de la Destrucción",
        "quote": "¡Pronto los secretos del Castillo Grayskull me pertenecerán!",
        "flavor_quote_author": "Skeletor",
        "special_move": "Orbe Maldito de Havoc",
        "lore": "Amo despiadado de Snake Mountain y hechicero supremo de las artes oscuras. No se detendrá ante nada hasta doblegar a Eternia bajo su yugo de terror.",
        "source_url": "https://he-man.fandom.com/wiki/Skeletor"
    },
    "battle armor skeletor": {
        "subtitle": "Tirano Acorazado de la Destrucción",
        "quote": "¡Ni siquiera la Espada del Poder puede quebrar mi acero oscuro!",
        "flavor_quote_author": "Skeletor",
        "special_move": "Defensa de Hueso Maldito",
        "lore": "Protegido por una coraza encantada con hechicería infernal para resistir las acometidas directas de He-Man en el fragor de la guerra eterna.",
        "source_url": "https://he-man.fandom.com/wiki/Battle_Armor_Skeletor"
    },
    "dragon blaster skeletor": {
        "subtitle": "Amo del Dragón Venenoso",
        "quote": "¡Huid ante el aliento abrasador de mi dragón cautivo!",
        "flavor_quote_author": "Skeletor",
        "special_move": "Rociada de Ácido Dracónico",
        "lore": "Encadenando a una temible cría de dragón místico a su espalda, Skeletor dispara chorros paralizantes de agua ponzoñosa contra sus adversarios.",
        "source_url": "https://he-man.fandom.com/wiki/Dragon_Blaster_Skeletor"
    },
    "terror claws skeletor": {
        "subtitle": "Monstruo de las Garras Asesinas",
        "quote": "¡Mis garras desgarrarán el manto de Grayskull!",
        "flavor_quote_author": "Skeletor",
        "special_move": "Zarpazo de Acero Desgarrador",
        "lore": "Equipado con enormes garras de combate biomecánicas y una calavera oscilante que aterroriza a quien se atreva a cruzar su camino.",
        "source_url": "https://he-man.fandom.com/wiki/Terror_Claws_Skeletor"
    },

    # ── GUERREROS HEROICOS ──
    "teela": {
        "subtitle": "Capitana de la Guardia Real",
        "quote": "¡Nuestra lealtad a Grayskull es nuestro mayor escudo!",
        "flavor_quote_author": "Teela",
        "special_move": "Estocada Táctica de la Cobra",
        "lore": "Valiente capitana de la guardia del palacio y experta maestra en artes marciales. Desconoce que en su sangre fluye el místico destino de Grayskull.",
        "source_url": "https://he-man.fandom.com/wiki/Teela"
    },
    "man-at-arms": {
        "subtitle": "Maestro de Armas e Ingeniero Real",
        "quote": "La ciencia y la estrategia ganan tantas batallas como el coraje.",
        "flavor_quote_author": "Duncan",
        "special_move": "Ráfaga Fotónica Man-At-Arms",
        "lore": "Consejero de confianza del rey Randor y mentor táctico de He-Man. Diseña y forja las armas, armaduras y vehículos que salvan a Eternia.",
        "source_url": "https://he-man.fandom.com/wiki/Man-At-Arms"
    },
    "stratos": {
        "subtitle": "Señor Alado de Avion",
        "quote": "¡Desde las alturas, ningún enemigo escapa a los cielos de Avion!",
        "flavor_quote_author": "Stratos",
        "special_move": "Picado Aéreo Supersónico",
        "lore": "Líder de la civilización voladora de Avion y poderoso aliado de He-Man. Surca los vientos con sus propulsores y desata ataques fulminantes desde el aire.",
        "source_url": "https://he-man.fandom.com/wiki/Stratos"
    },
    "ram man": {
        "subtitle": "El Ariete Humano",
        "quote": "¡Abran paso o derribaré esta fortaleza con mi cabeza!",
        "flavor_quote_author": "Ram Man",
        "special_move": "Embestida de Acero Macizo",
        "lore": "Leal guerrero provisto de resortes en sus piernas y un yelmo reforzado, capaz de tumbar las puertas y murallas más sólidas de un solo salto demoledor.",
        "source_url": "https://he-man.fandom.com/wiki/Ram_Man"
    },
    "fisto": {
        "subtitle": "El Hombre del Puño de Acero",
        "quote": "¡Un solo golpe de mi puño basta para quebrar cualquier defensa!",
        "flavor_quote_author": "Fisto",
        "special_move": "Golpe demoledor de Acero",
        "lore": "Guerrero legendario del bosque con un colosal puño metálico. Su fuerza demoledora y su gran corazón lo convierten en un bastión heroico.",
        "source_url": "https://he-man.fandom.com/wiki/Fisto"
    },
    "clamp champ": {
        "subtitle": "Guardián de la Tenaza de Captura",
        "quote": "¡Una vez atrapado en mi tenaza, no hay escapatoria!",
        "flavor_quote_author": "Clamp Champ",
        "special_move": "Presa de Tenaza Hidráulica",
        "lore": "Maestro del rastreo y el sigilo, designado como escolta de la realeza eterniana. Su arma de pinza inmoviliza a las criaturas más fieras.",
        "source_url": "https://he-man.fandom.com/wiki/Clamp_Champ"
    },
    "buzz-off": {
        "subtitle": "Guerrero Insecto de Andreenos",
        "quote": "¡Nuestra colmena defiende la libertad de Eternia!",
        "flavor_quote_author": "Buzz-Off",
        "special_move": "Aguijonazo Ácido Sónico",
        "lore": "Líder de la raza de abejas humanoides de Andreenos. Sus ojos multifacetados y sus alas zumbantes le otorgan una puntería y vigilancia insuperables.",
        "source_url": "https://he-man.fandom.com/wiki/Buzz-Off"
    },
    "moss man": {
        "subtitle": "Señor de la Naturaleza",
        "quote": "La flora de Eternia escucha mi llamada.",
        "flavor_quote_author": "Moss Man",
        "special_move": "Camuflaje de Esporas Vivas",
        "lore": "Entidad milenaria compuesta de follaje y musgo viviente. Capaz de fusionarse con cualquier planta y manipular la vegetación para frenar a los invasores.",
        "source_url": "https://he-man.fandom.com/wiki/Moss_Man"
    },
    "roboto": {
        "subtitle": "Guerrero Mecánico Heroico",
        "quote": "Sistemas ópticos y engranajes listos para el combate.",
        "flavor_quote_author": "Roboto",
        "special_move": "Rotación de Cañón Intercambiable",
        "lore": "Robot con conciencia construido por Man-At-Arms. Su torso transparente muestra sus engranajes en movimiento mientras intercambia manos de hacha, garra y láser.",
        "source_url": "https://he-man.fandom.com/wiki/Roboto"
    },
    "zodac": {
        "subtitle": "Ejecutor Cósmico",
        "quote": "El equilibrio del universo debe prevalecer sobre todo conflicto.",
        "flavor_quote_author": "Zodac",
        "special_move": "Juicio Cósmico Neutral",
        "lore": "Miembro de los Guardianes Cósmicos que viaja en su silla flotante por las estrellas, vigilando que ninguna fuerza altere la armonía del universo.",
        "source_url": "https://he-man.fandom.com/wiki/Zodac"
    },

    # ── GUERREROS DEL MAL ──
    "trap jaw": {
        "subtitle": "Mago de las Armas con Mandíbula de Hierro",
        "quote": "¡Pruébate ante mi garra, mi gancho o mi cañón láser!",
        "flavor_quote_author": "Trap Jaw",
        "special_move": "Mordisco Triturador de Acero",
        "lore": "Ciborg criminal con una mandíbula mecánica capaz de morder cualquier metal. Su brazo robótico acopla múltiples herramientas letales.",
        "source_url": "https://he-man.fandom.com/wiki/Trap_Jaw"
    },
    "tri-klops": {
        "subtitle": "Espía de los Tres Ojos",
        "quote": "¡Veo todo en la oscuridad, en infrarrojo y a través de los muros!",
        "flavor_quote_author": "Tri-Klops",
        "special_move": "Rayo Óptico Destructor",
        "lore": "Mercenario y maestro de armas con un visor giratorio de tres lentes ópticas. Sus descargas oculares derriten rocas y detectan emboscadas.",
        "source_url": "https://he-man.fandom.com/wiki/Tri-Klops"
    },
    "beast man": {
        "subtitle": "Señor de las Fieras",
        "quote": "¡Los monstruos salvajes de Eternia obedecen mi látigo!",
        "flavor_quote_author": "Beast Man",
        "special_move": "Aullido de Dominación Salvaje",
        "lore": "Criatura brutal cubierta de pelaje anaranjado con el poder telepático de someter y controlar a las bestias más peligrosas de las selvas y mazmorras.",
        "source_url": "https://he-man.fandom.com/wiki/Beast_Man"
    },
    "evil-lyn": {
        "subtitle": "Señora del Caos y la Magia Oscura",
        "quote": "Los necios confían en la fuerza bruta; la verdadera reina es la magia.",
        "flavor_quote_author": "Evil-Lyn",
        "special_move": "Descarga de Sombras Arcanas",
        "lore": "Hechicera calculadora y aliada inestable de Skeletor. Con su orbe místico conjura ilusiones y maldiciones mientras conspira por su propio poder.",
        "source_url": "https://he-man.fandom.com/wiki/Evil-Lyn"
    },
    "mer-man": {
        "subtitle": "Soberano de los Océanos de Eternia",
        "quote": "¡Las profundidades abisales tragarán a la superficie!",
        "flavor_quote_author": "Mer-Man",
        "special_move": "Tsunami del Tridente Marino",
        "lore": "Rey de los mares y señor de los monstruos submarinos de Eternia. Armado con su espada de coral, acecha desde las costas para servir a Skeletor.",
        "source_url": "https://he-man.fandom.com/wiki/Mer-Man"
    },
    "clawful": {
        "subtitle": "Guerrero Crustáceo del Mal",
        "quote": "¡Una vez que mi pinza se cierra, nada en Eternia puede abrirla!",
        "flavor_quote_author": "Clawful",
        "special_move": "Presa Trituradora de Pinza",
        "lore": "Humanoide con coraza de crustáceo y una pinza derecha gigante de fuerza colosal. Sirviente leal de Skeletor que ataca con brutalidad marina.",
        "source_url": "https://he-man.fandom.com/wiki/Clawful"
    },
    "whiplash": {
        "subtitle": "El Monstruo de la Cola Látigo",
        "quote": "¡Un coletazo mío basta para quebrar las defensas de Grayskull!",
        "flavor_quote_author": "Whiplash",
        "special_move": "Coletazo Sísmico Demoletor",
        "lore": "Criatura reptiliana dotada de una cola maciza y musculosa que azota como un ariete de guerra, derribando guerreros y vehículos enteros.",
        "source_url": "https://he-man.fandom.com/wiki/Whiplash"
    },
    "jitsu": {
        "subtitle": "Maestro del Golpe de Kárate Dorado",
        "quote": "¡Mi mano dorada parte el acero más templado!",
        "flavor_quote_author": "Jitsu",
        "special_move": "Tajo de Kárate Destructor",
        "lore": "Maestro de artes marciales diabólicas y rival jurado de Fisto. Su enorme mano derecha forjada en metal dorado puede quebrar cualquier armadura.",
        "source_url": "https://he-man.fandom.com/wiki/Jitsu"
    },
    "webstor": {
        "subtitle": "Amo de las Telarañas de Escape",
        "quote": "¡Nadie escapa de las redes que tejo en la oscuridad!",
        "flavor_quote_author": "Webstor",
        "special_move": "Trampa de Seda Asfixiante",
        "lore": "Astuto humanoide arácnido con una mochila de tirolina retráctil que le permite escalar paredes verticales e infiltrarse en cualquier fortaleza.",
        "source_url": "https://he-man.fandom.com/wiki/Webstor"
    },
    "kobra khan": {
        "subtitle": "La Serpiente del Aliento Somnífero",
        "quote": "¡Inhala la bruma que apaga tu voluntad!",
        "flavor_quote_author": "Kobra Khan",
        "special_move": "Vaho Paralizante de Cobra",
        "lore": "Reptiliano traicionero que expulsa una densa niebla somnífera por su boca ensanchada, dejando a sus víctimas completamente indefensas.",
        "source_url": "https://he-man.fandom.com/wiki/Kobra_Khan"
    },
    "spikor": {
        "subtitle": "El Herrero de las Espinas de Acero",
        "quote": "¡Atrévete a tocarme y te perforarán mil púas!",
        "flavor_quote_author": "Spikor",
        "special_move": "Erupción de Espinas Punzantes",
        "lore": "Guerrero cubierto de afiladas púas impenetrables y dotado de un tridente extensible en su brazo. Forja armas letales para el ejército de Skeletor.",
        "source_url": "https://he-man.fandom.com/wiki/Spikor"
    },
    "stinkor": {
        "subtitle": "El Monstruo de la Pestilencia Diabólica",
        "quote": "¡Huid o asfixiaos en mi nube de gas insoportable!",
        "flavor_quote_author": "Stinkor",
        "special_move": "Neblina Nauseabunda",
        "lore": "Mutante con aspecto de zorrillo que emite un hedor tan asfixiante que incapacita al instante a los guerreros más experimentados de Grayskull.",
        "source_url": "https://he-man.fandom.com/wiki/Stinkor"
    },
    "two-bad": {
        "subtitle": "Estratega de Doble Cabeza",
        "quote": "¡Doble fuerza para aplastar, aunque no nos pongamos de acuerdo!",
        "flavor_quote_author": "Tuvar & Baddhra",
        "special_move": "Doble Cabezazo Sincronizado",
        "lore": "Criatura fusionada con dos cabezas rivales (Tuvar y Baddhra) que riñen constantemente entre sí pero desatan una fuerza física devastadora.",
        "source_url": "https://he-man.fandom.com/wiki/Two-Bad"
    },

    # ── LA HORDA DEL TERROR ──
    "hordak": {
        "subtitle": "Líder Despiadado de la Horda del Terror",
        "quote": "¡Ni He-Man ni Skeletor podrán frenar la conquista de la Horda!",
        "flavor_quote_author": "Hordak",
        "special_move": "Transformación de Cañón Mecánico",
        "lore": "Antiguo maestro de Skeletor y conquistador supremo de mundos. Maestro de la magia negra y la ciencia cyborg, capaz de transformar su cuerpo en armamento.",
        "source_url": "https://he-man.fandom.com/wiki/Hordak"
    },
    "grizzlor": {
        "subtitle": "La Bestia Peluda de la Horda",
        "quote": "¡Rugido salvaje que quiebra la roca viva!",
        "flavor_quote_author": "Grizzlor",
        "special_move": "Embestida de Furia Parda",
        "lore": "Monstruo de pelaje denso e indomable, utilizado por Hordak como fuerza de choque bruta para infundir pánico absoluto en el campo de batalla.",
        "source_url": "https://he-man.fandom.com/wiki/Grizzlor"
    },
    "leech": {
        "subtitle": "El Maestro Succionador de Energía",
        "quote": "¡Drenaré cada gota de poder de tu cuerpo!",
        "flavor_quote_author": "Leech",
        "special_move": "Succión Sanguínea de Poder",
        "lore": "Criatura anfibia con ventosas en manos y boca que succiona la fuerza vital y la magia de sus enemigos, debilitando incluso al mismísimo He-Man.",
        "source_url": "https://he-man.fandom.com/wiki/Leech"
    },
    "mantenna": {
        "subtitle": "Espía de Ojos Telescópicos",
        "quote": "¡Mis ojos saltan para detectar a los rebeldes a leguas de distancia!",
        "flavor_quote_author": "Mantenna",
        "special_move": "Rayo Hipnótico Ocular",
        "lore": "Explorador de cuatro patas de la Horda con ojos saltones extensibles que disparan rayos paralizantes e hipnóticos sobre sus presas.",
        "source_url": "https://he-man.fandom.com/wiki/Mantenna"
    },

    # ── LOS HOMBRES SERPIENTE ──
    "king hiss": {
        "subtitle": "Temible Rey de los Hombres Serpiente",
        "quote": "¡Bajo la piel humana duerme el verdadero terror ofídico!",
        "flavor_quote_author": "Rey Hiss",
        "special_move": "Metamorfosis de Ofidios Venenosos",
        "lore": "Monarca ancestral de los Hombres Serpiente. Oculta bajo su apariencia de noble una masa letal de serpientes entrelazadas listas para devorar a Eternia.",
        "source_url": "https://he-man.fandom.com/wiki/King_Hiss"
    },
    "rattlor": {
        "subtitle": "La Serpiente del Cuello Extensible",
        "quote": "¡Mi cascabel anuncia el fin de tus días!",
        "flavor_quote_author": "Rattlor",
        "special_move": "Golpe de Cuello Percutor",
        "lore": "Feroz guerrero serpiente con un cuello telescópico que dispara su cabeza como un proyectil demoledor, mientras su cascabel emite una advertencia siniestra.",
        "source_url": "https://he-man.fandom.com/wiki/Rattlor"
    },
    "tung lashor": {
        "subtitle": "El Monstruo de la Lengua Venenosa",
        "quote": "¡Mi lengua te alcanzará antes de que puedas pestañear!",
        "flavor_quote_author": "Tung Lashor",
        "special_move": "Latigazo de Lengua Ponzoñosa",
        "lore": "Reptiliano temible con una larguísima lengua retráctil cubierta de una toxina paralizante que desarma a sus contrincantes al instante.",
        "source_url": "https://he-man.fandom.com/wiki/Tung_Lashor"
    },

    # ── VEHÍCULOS, MONTURAS & PLAYSETS ──
    "battle cat": {
        "subtitle": "Tigre de Batalla Acorazado",
        "quote": "¡Ruge el defensor felino de Grayskull!",
        "flavor_quote_author": "Cringer / Battle Cat",
        "special_move": "Zarpazo de Titán Acorazado",
        "lore": "Fiel montura y compañero de He-Man. Transformado por el místico poder de Grayskull en un gigantesco tigre acorazado con garras letales.",
        "source_url": "https://he-man.fandom.com/wiki/Battle_Cat"
    },
    "panthor": {
        "subtitle": "Pantera Salvaje del Mal",
        "quote": "El sigilo de la noche a las órdenes de Snake Mountain.",
        "flavor_quote_author": "Skeletor",
        "special_move": "Embestida de Sombras Carmesí",
        "lore": "Feroz pantera púrpura de pelaje sedoso y garras afiladas como navajas, montura favorita de Skeletor para sembrar el terror por las planicies eternianas.",
        "source_url": "https://he-man.fandom.com/wiki/Panthor"
    },
    "castle grayskull": {
        "subtitle": "Fortaleza del Misterio y del Poder",
        "quote": "Quien posea los secretos de este castillo dominará el cosmos.",
        "flavor_quote_author": "La Hechicera",
        "special_move": "Foco del Poder Infinito",
        "lore": "Antigua fortaleza ancestral de piedra verde con fachada de calavera. En su interior se custodia el poder supremo del universo y el trono del saber.",
        "source_url": "https://he-man.fandom.com/wiki/Castle_Grayskull"
    },
    "snake mountain": {
        "subtitle": "Fortaleza del Caos y la Magia Oscura",
        "quote": "Las fauces de la montaña serpiente engullirán a la luz.",
        "flavor_quote_author": "Skeletor",
        "special_move": "Alarido de la Roca Maldita",
        "lore": "Siniestro bastión esculpido en roca basáltica con forma de serpiente gigante rodeada de cascadas de lava. El cuartel general del mal en Eternia.",
        "source_url": "https://he-man.fandom.com/wiki/Snake_Mountain"
    },
    "wind raider": {
        "subtitle": "Vehículo Asaltante del Viento",
        "quote": "¡Dominio de los cielos y tierra de Eternia!",
        "flavor_quote_author": "Man-At-Arms",
        "special_move": "Lanzamiento de Ancla Arpón",
        "lore": "Ágil nave de asalto aéreo diseñada por Man-At-Arms, equipada con alas orientables y un potente cabrestante con ancla para maniobras tácticas extremas.",
        "source_url": "https://he-man.fandom.com/wiki/Wind_Raider"
    },
    "land shark": {
        "subtitle": "El Tiburón Terrestre Devorador",
        "quote": "¡Sus fauces de acero devoran todo a su paso!",
        "flavor_quote_author": "Skeletor",
        "special_move": "Mordisco Móvil Triturador",
        "lore": "Tanque acorazado con forma de tiburón cuyas mandíbulas de metal se abren y cierran implacablemente al rodar, aplastando los obstáculos de Snake Mountain.",
        "source_url": "https://he-man.fandom.com/wiki/Land_Shark"
    },
    "stridor": {
        "subtitle": "Corcel Blindado Mecánico",
        "quote": "¡El relincho del caballo de guerra de Grayskull!",
        "flavor_quote_author": "Man-At-Arms",
        "special_move": "Bombardeo de Cascos Láser",
        "lore": "Caballo cibernético provisto de blindaje integral y cañones frontales gemelos, capaz de galopar a velocidades supersónicas sobre cualquier terreno hostil.",
        "source_url": "https://he-man.fandom.com/wiki/Stridor"
    },
    "point dread": {
        "subtitle": "Torre de Vigilancia y Caza Talon",
        "quote": "¡Vigilancia perimetral en la cima del mundo!",
        "flavor_quote_author": "La Hechicera",
        "special_move": "Despegue Táctico Talon Fighter",
        "lore": "Puesto avanzado de radar que puede acoplarse a Castle Grayskull y alberga en su cima la formidable nave de combate Talon Fighter.",
        "source_url": "https://he-man.fandom.com/wiki/Point_Dread"
    }
}


class ProductLoreSeedService:
    """
    Servicio de sembrado automático y enriquecimiento de lore para figuras Origins.
    """

    @classmethod
    def match_cardback_lore(cls, product_name: str) -> Optional[Dict[str, str]]:
        """Busca en el diccionario de cardbacks por aproximación inteligente de nombre."""
        p_name = product_name.lower().strip()
        
        # 1. Búsqueda exacta / por clave de subcadena más larga
        matches = []
        for key, data in CARDBACK_BIOS_ORIGINS.items():
            if key in p_name:
                matches.append((len(key), data))
        
        if matches:
            # Seleccionar la coincidencia más específica (ej: 'battle armor he-man' antes que 'he-man')
            matches.sort(key=lambda x: x[0], reverse=True)
            return matches[0][1]
            
        return None

    @classmethod
    def generate_default_lore_for_product(cls, product: ProductModel, db: Session) -> Dict[str, Any]:
        """
        Genera el paquete de lore completo combinando:
        1. Diccionario de cardbacks oficiales de Mattel en español.
        2. Fallback a CharacterLoreModel mediante character_slug.
        3. Fallback heurístico a la base de datos canónica motu_canon_database.
        """
        canon_profile = resolve_motu_profile(product.name, product.sub_category)
        cardback = cls.match_cardback_lore(product.name)

        # Buscar si existe character_lore
        char_lore: Optional[CharacterLoreModel] = None
        if product.character_slug:
            char_lore = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == product.character_slug).first()

        # Consolidar campos con prioridad: Cardback oficial > Character Lore > Perfil Canónico
        subtitle = None
        if cardback and cardback.get("subtitle"):
            subtitle = cardback["subtitle"]
        elif char_lore and char_lore.subtitle:
            subtitle = char_lore.subtitle
        elif product.sub_category:
            subtitle = f"Colección {product.sub_category}"
        else:
            subtitle = "Campeón de Nueva Eternia"

        quote = None
        if cardback and cardback.get("quote"):
            quote = cardback["quote"]
        elif char_lore and char_lore.quote:
            quote = char_lore.quote
        else:
            quote = f"¡Por la gloria y el destino de {canon_profile.get('canonical_name', 'Eternia')}!"

        flavor_quote_author = None
        if cardback and cardback.get("flavor_quote_author"):
            flavor_quote_author = cardback["flavor_quote_author"]
        elif char_lore and (char_lore.flavor_quote_author or char_lore.canonical_name):
            flavor_quote_author = char_lore.flavor_quote_author or char_lore.canonical_name
        else:
            flavor_quote_author = canon_profile.get("canonical_name", product.name)

        lore_text = ""
        if cardback and cardback.get("lore"):
            lore_text = cardback["lore"]
        elif char_lore and char_lore.lore:
            lore_text = char_lore.lore
        else:
            lore_text = canon_profile.get("lore", f"Figura coleccionable oficial de la línea {product.sub_category or 'Masters of the Universe Origins'}.")

        special_move = ""
        if cardback and cardback.get("special_move"):
            special_move = cardback["special_move"]
        elif char_lore and char_lore.special_move:
            special_move = char_lore.special_move
        else:
            special_move = canon_profile.get("special_move", "Poder Ancestral de Grayskull")

        stats = canon_profile.get("stats", {})
        fuerza = char_lore.fuerza if char_lore else stats.get("fuerza", 85)
        magia = char_lore.magia if char_lore else stats.get("magia", 75)
        defensa = char_lore.defensa if char_lore else stats.get("defensa", 85)
        agilidad = char_lore.agilidad if char_lore else stats.get("agilidad", 85)

        faction = char_lore.faction if char_lore else canon_profile.get("faction", "Guerreros Heroicos")
        theme_key = char_lore.theme_key if char_lore else canon_profile.get("frame_theme", "castle_grayskull")
        type_line = char_lore.type_line if char_lore else canon_profile.get("type_line", "Criatura Legendaria — Guerrero")
        source_url = cardback.get("source_url") if cardback else (char_lore.source_url if char_lore else None)

        return {
            "product_id": product.id,
            "canonical_name": canon_profile.get("canonical_name", product.name),
            "subtitle": subtitle,
            "faction": faction,
            "theme_key": theme_key,
            "type_line": type_line,
            "special_move": special_move,
            "quote": quote,
            "flavor_quote_author": flavor_quote_author,
            "lore": lore_text,
            "source_url": source_url,
            "text_color": "#FFFFFF",
            "card_version": "showcase",
            "mana_cost": "{2}{W}{W}",
            "fuerza": fuerza,
            "magia": magia,
            "defensa": defensa,
            "agilidad": agilidad,
            "is_customized": False
        }

    @classmethod
    def seed_origins_products(cls, db: Session, force: bool = False) -> Dict[str, int]:
        """
        Siembra y asegura que el 100% de los muñecos de Origins (is_vintage == False)
        tengan su registro de ProductLoreModel activo.
        """
        # REGLA ESTRICTA: Solo productos Origins (is_vintage == False)
        origins_products = db.query(ProductModel).filter(
            (ProductModel.is_vintage == False) | (ProductModel.is_vintage.is_(None))
        ).all()

        total = len(origins_products)
        created = 0
        updated = 0
        skipped = 0

        for p in origins_products:
            existing = db.query(ProductLoreModel).filter(ProductLoreModel.product_id == p.id).first()

            if existing:
                if existing.is_customized and not force:
                    skipped += 1
                    continue
                # Actualizar si no fue personalizado a mano
                data = cls.generate_default_lore_for_product(p, db)
                for k, v in data.items():
                    if k != "is_customized":
                        setattr(existing, k, v)
                updated += 1
            else:
                data = cls.generate_default_lore_for_product(p, db)
                new_lore = ProductLoreModel(**data)
                db.add(new_lore)
                created += 1

        db.commit()
        logger.info(f"Grimorio Lore Origins :: Sembrado completado ({created} creados, {updated} actualizados, {skipped} preservados).")
        return {"total_origins": total, "created": created, "updated": updated, "skipped": skipped}
