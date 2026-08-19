"""
Base de Datos Canónica de Masters of the Universe para el Oráculo de Nueva Eternia.
Contiene:
- Matriz de más de 50 ataques especiales preconfigurados asociados a armas y accesorios.
- Enciclopedia de Lore canónico y perfiles RPG para personajes de MOTU, Origins, Masterverse y Crossovers.
- Mapeo de Facciones traducidas al castellano con temas de marco (Grayskull, Snake Mountain, Horda, etc.).
"""

from typing import Dict, Any, Optional, List

# 1. MATRIZ DE ATAQUES ESPECIALES MOTU POR TIPO DE ARMA / ACCESORIO
ATTACK_MATRIX: Dict[str, List[str]] = {
    "power_sword": [
        "Furia del Relámpago de Grayskull",
        "Tajo Cósmico de Luz Ancestral",
        "Vórtice Solar de Eternia",
        "Estocada del Poder Infinito",
        "Corte Hendidor de Titanes"
    ],
    "sword_of_omens": [
        "Furia del Ojo de Thundera",
        "Visión de Augurio Iluminador",
        "Ráfaga Felina de Thundera",
        "Tajo de la Garra Escarlata",
        "Poder del Augurio Supremo"
    ],
    "havoc_staff": [
        "Descarga de Sombras Arcanas",
        "Orbe Maldito de Snake Mountain",
        "Juicio Espectral de Havoc",
        "Rayo Nigromántico del Caos",
        "Invocación del Velo Demoníaco"
    ],
    "battle_axe": [
        "Hendidura Doble de Acero Eterniano",
        "Torbellino Devastador de Grayskull",
        "Filo Sísmico de Batalla",
        "Golpe Decapitador de Titanes",
        "Quebrantahuesos de Hierro"
    ],
    "laser_blaster": [
        "Ráfaga Fotónica Man-At-Arms",
        "Descarga de Iones de Plasma",
        "Disparo Térmico Perforante",
        "Pulso Láser de Alta Densidad",
        "Bombardeo Óptico Táctico"
    ],
    "claws_beast": [
        "Zarpazo Titánico de la Jungla",
        "Desgarro Feroz de la Selva Carmesí",
        "Embestida Bestial Salvaje",
        "Mordisco Destructor de Panthor",
        "Furia Dentada de Eternia"
    ],
    "magic_sorcery": [
        "Escudo del Halcón Místico",
        "Lanza de Luz Arcana de Zoar",
        "Tormenta Ilusoria de Subternia",
        "Onda Psíquica de los Antiguos",
        "Canto de Protección de Grayskull"
    ],
    "ram_mace": [
        "Impacto de Ariete Inamovible",
        "Martillazo Sísmico de Titanio",
        "Onda de Choque Terrestre",
        "Golpe Demoledor de Murallas",
        "Cabezazo de Acero Macizo"
    ],
    "horde_crossbow": [
        "Dardo Perforador de Etheria",
        "Flecha de Plasma Carmesí de la Horda",
        "Disparo de Perno Sónico",
        "Saeta Vampírica de Hordak",
        "Andanada de Espinas Asfixiantes"
    ],
    "mechanical_trap": [
        "Presa Hidráulica Trituradora",
        "Mordisco de Mandíbula de Acero",
        "Garra de Extensión Asesina",
        "Láser Óptico de Rastreo Letal",
        "Sierra Circular de Alta Revolución"
    ],
    "snake_venom": [
        "Azote Ofídico Venenoso",
        "Mordisco Asfixiante del Rey Hiss",
        "Chorro Ácido Corrosivo",
        "Estrangulamiento de Pitón Arcano",
        "Hipnosis de la Serpiente Carmesí"
    ],
    "water_ocean": [
        "Tsunami de las Profundidades de Rakash",
        "Tridente de Marea Hirviente",
        "Corriente Abisal Devastadora",
        "Invocación del Monstruo Marino",
        "Espuma Asfixiante de los Océanos"
    ],
    "cosmic_flight": [
        "Picado Aéreo de Avión",
        "Ráfaga de Viento Esmeralda",
        "Corte Alar Supersónico",
        "Descarga Cósmica de Zodac",
        "Bucle Cinético Estratosférico"
    ]
}

ALL_SPECIAL_ATTACKS: List[str] = [atk for sublist in ATTACK_MATRIX.values() for atk in sublist]

# 2. ENCICLOPEDIA CANÓNICA MOTU
# Mapeo exhaustivo de personajes con su facción en castellano, estilo de marco y stats balanceados.
MOTU_LORE_ENCYCLOPEDIA: Dict[str, Dict[str, Any]] = {
    # ── GUERREROS HEROICOS (CASTLE GRAYSKULL) ──
    "he-man": {
        "canonical_name": "He-Man",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Legendaria — Guerrero Heroico",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "grayskull", "gold", "sword"],
        "lore": "Defensor supremo de los secretos de Castle Grayskull y campeón indiscutible de Eternia. Guiado por la Espada del Poder, su fuerza inquebrantable protege el universo de las garras de la oscuridad.",
        "stats": {"fuerza": 99, "magia": 88, "defensa": 95, "agilidad": 90},
        "special_move": "Furia del Relámpago de Grayskull",
        "weapon_type": "power_sword"
    },
    "battle armor he-man": {
        "canonical_name": "He-Man (Battle Armor)",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Legendaria — Guerrero Heroico",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "grayskull", "gold", "axe"],
        "lore": "Equipado con la coraza mística forjada en las forjas sagradas para absorber los impactos más devastadores. Cuando el combate arrecia en Eternia, este titán resiste cualquier asedio.",
        "stats": {"fuerza": 99, "magia": 86, "defensa": 99, "agilidad": 87},
        "special_move": "Hendidura Doble de Acero Eterniano",
        "weapon_type": "battle_axe"
    },
    "prince adam": {
        "canonical_name": "Príncipe Adam",
        "faction": "Guerreros Heroicos",
        "type_line": "Héroe de la Realeza — Heredero de Grayskull",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "gold"],
        "lore": "Heredero legítimo del trono real de Eternia y custodio secreto del mayor poder del cosmos. Bajo su aparente calma cortesana reside la voluntad del campeón del universo.",
        "stats": {"fuerza": 78, "magia": 84, "defensa": 79, "agilidad": 86},
        "special_move": "Destello de la Espada de Grayskull",
        "weapon_type": "power_sword"
    },
    "teela": {
        "canonical_name": "Teela",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Legendaria — Capitana de la Guardia",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "gold", "sword"],
        "lore": "Capitana invicta de la Guardia Real y virtuosa estratega en las artes del combate cuerpo a cuerpo. Heredera del misticismo de Grayskull, lidera las tropas reales con valentía indomable.",
        "stats": {"fuerza": 85, "magia": 82, "defensa": 88, "agilidad": 94},
        "special_move": "Estocada Táctica de la Cobra",
        "weapon_type": "power_sword"
    },
    "man-at-arms": {
        "canonical_name": "Man-At-Arms",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Legendaria — Maestro de Armas",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "gold", "blaster"],
        "lore": "Maestro supremo de armas e ilustre inventor de las defensas mecánicas del Palacio de Eternia. Su ingenio tecnológico y su devoción fraternal protegen a la familia real en cada crisis.",
        "stats": {"fuerza": 88, "magia": 72, "defensa": 94, "agilidad": 80},
        "special_move": "Ráfaga Fotónica Man-At-Arms",
        "weapon_type": "laser_blaster"
    },
    "sorceress": {
        "canonical_name": "La Hechicera",
        "faction": "Guerreros Heroicos",
        "type_line": "Avatar Místico — Guardiana de Grayskull",
        "frame_theme": "castle_grayskull",
        "emblem": "sparkles",
        "mana_gems": ["grayskull", "grayskull", "arcane", "magic"],
        "lore": "Guardiana mística y alma viva de Castle Grayskull, canalizadora de la magia ancestral del cosmos. Su sabiduría milenaria guía a los campeones de la luz a través de las eras.",
        "stats": {"fuerza": 70, "magia": 99, "defensa": 90, "agilidad": 88},
        "special_move": "Escudo del Halcón Místico",
        "weapon_type": "magic_sorcery"
    },
    "stratos": {
        "canonical_name": "Stratos",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Legendaria — Soberano de Avion",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "air"],
        "lore": "Monarca de la ciudad alada de Avion y soberano de las corrientes de aire de Eternia. Con sus cohetes dorsales y su visión prodigiosa domina los cielos en la lucha contra el mal.",
        "stats": {"fuerza": 84, "magia": 75, "defensa": 82, "agilidad": 98},
        "special_move": "Picado Aéreo de Avion",
        "weapon_type": "cosmic_flight"
    },
    "ram man": {
        "canonical_name": "Ram Man",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Legendaria — Ariete de Grayskull",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "earth"],
        "lore": "Ariete humano indestructible con corazas de acero y resortes hidráulicos. Ninguna puerta de fortaleza ni formación enemiga puede frenar su avance demoledor.",
        "stats": {"fuerza": 94, "magia": 55, "defensa": 98, "agilidad": 72},
        "special_move": "Impacto de Ariete Inamovible",
        "weapon_type": "ram_mace"
    },
    "battle cat": {
        "canonical_name": "Battle Cat",
        "faction": "Guerreros Heroicos",
        "type_line": "Bestia Legendaria — Tigre de Batalla",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "grayskull", "claws"],
        "lore": "Tigre de combate acorazado y fiel montura de batalla de He-Man en el fragor de la contienda. Con su rugido atronador y garras titánicas dispersa ejércitos enteros.",
        "stats": {"fuerza": 96, "magia": 74, "defensa": 92, "agilidad": 93},
        "special_move": "Desgarro Feroz de la Selva Carmesí",
        "weapon_type": "claws_beast"
    },
    "moss man": {
        "canonical_name": "Moss Man",
        "faction": "Guerreros Heroicos",
        "type_line": "Espíritu Ancestral — Guardián de la Flora",
        "frame_theme": "castle_grayskull",
        "emblem": "sparkles",
        "mana_gems": ["grayskull", "nature"],
        "lore": "Señor ancestral de la flora eterniana capaz de fusionarse con la vegetación y controlar las raíces vivientes. Guardián pacífico que despierta una furia imparable ante la tiranía.",
        "stats": {"fuerza": 88, "magia": 92, "defensa": 90, "agilidad": 84},
        "special_move": "Enredo de Raíces Primordiales",
        "weapon_type": "magic_sorcery"
    },
    "roboto": {
        "canonical_name": "Roboto",
        "faction": "Guerreros Heroicos",
        "type_line": "Autómata Legendario — Guerrero Mecánico",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "tech"],
        "lore": "Guerrero mecánico consciente dotado de un corazón de compasión y engranajes de precisión infinita. Sus aditamentos intercambiables lo convierten en un arsenal andante.",
        "stats": {"fuerza": 91, "magia": 60, "defensa": 96, "agilidad": 78},
        "special_move": "Presa Hidráulica Trituradora",
        "weapon_type": "mechanical_trap"
    },
    "fisto": {
        "canonical_name": "Fisto",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Legendaria — Gladiador de Grayskull",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "metal"],
        "lore": "Guerrero formidable con un puño de acero indestructible forjado para quebrar murallas. Su lealtad a Grayskull se demuestra en cada golpe demoledor.",
        "stats": {"fuerza": 96, "magia": 62, "defensa": 94, "agilidad": 82},
        "special_move": "Golpe Demoledor de Murallas",
        "weapon_type": "ram_mace"
    },
    "clamp champ": {
        "canonical_name": "Clamp Champ",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Legendaria — Guardaespaldas Real",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "steel"],
        "lore": "Maestro capturador y guardaespaldas personal de la familia real. Su gigantesca pinza electromecánica inmoviliza a los enemigos más pesados al instante.",
        "stats": {"fuerza": 92, "magia": 65, "defensa": 93, "agilidad": 88},
        "special_move": "Presa Hidráulica Trituradora",
        "weapon_type": "mechanical_trap"
    },
    "sy-klone": {
        "canonical_name": "Sy-Klone",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Legendaria — Señor del Viento",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "wind"],
        "lore": "Guerrero cinético capaz de rotar su torso a velocidades supersónicas, generando torbellinos huracanados que dispersan a las legiones del mal.",
        "stats": {"fuerza": 87, "magia": 78, "defensa": 88, "agilidad": 97},
        "special_move": "Torbellino Devastador de Grayskull",
        "weapon_type": "cosmic_flight"
    },
    "buzz-off": {
        "canonical_name": "Buzz-Off",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Legendaria — Guerrero Andreenido",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "flight"],
        "lore": "Líder de la colmena Andreenida de Eternia. Con sus alas zumbantes y ojos facetados proporciona vigilancia aérea y ataques certeros desde las alturas.",
        "stats": {"fuerza": 86, "magia": 68, "defensa": 85, "agilidad": 96},
        "special_move": "Disparo Térmico Perforante",
        "weapon_type": "laser_blaster"
    },
    "mekaneck": {
        "canonical_name": "Mekaneck",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Legendaria — Explorador Real",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "vision"],
        "lore": "Explorador con un cuello biónico extensible capaz de divisar amenazas a kilómetros de distancia. Sus lentes periscópicos detectan cualquier trampa enemiga.",
        "stats": {"fuerza": 83, "magia": 60, "defensa": 86, "agilidad": 88},
        "special_move": "Láser Óptico de Rastreo Letal",
        "weapon_type": "laser_blaster"
    },

    # ── GUERREROS DIABÓLICOS (SNAKE MOUNTAIN) ──
    "skeletor": {
        "canonical_name": "Skeletor",
        "faction": "Guerreros Diabólicos",
        "type_line": "Señor Oscuro — Tirano de Snake Mountain",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "havoc", "dark", "sorcery"],
        "lore": "Señor de la destrucción y tirano nigromántico de Snake Mountain cuya sed de conquista amenaza la existencia. Empuñando el Báculo del Caos, canaliza las artes oscuras prohibidas de Subternia.",
        "stats": {"fuerza": 92, "magia": 99, "defensa": 88, "agilidad": 89},
        "special_move": "Descarga de Sombras Arcanas",
        "weapon_type": "havoc_staff"
    },
    "battle armor skeletor": {
        "canonical_name": "Skeletor (Battle Armor)",
        "faction": "Guerreros Diabólicos",
        "type_line": "Señor Oscuro — Tirano de Snake Mountain",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "havoc", "dark", "armor"],
        "lore": "Protegido por una armadura oscura blindada forjada en las cavernas sulfurosas del inframundo. Listo para liderar la invasión definitiva sobre las almenas de Grayskull.",
        "stats": {"fuerza": 94, "magia": 98, "defensa": 97, "agilidad": 86},
        "special_move": "Juicio Espectral de Havoc",
        "weapon_type": "havoc_staff"
    },
    "beast man": {
        "canonical_name": "Beast Man",
        "faction": "Guerreros Diabólicos",
        "type_line": "Criatura Legendaria — Guerrero Diabólico",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "blood", "beast"],
        "lore": "Señor salvaje de las bestias de Eternia y leal esbirro de Skeletor. Con su látigo ardiente y telepatía animal doblega a las criaturas más temibles de la Montaña de la Serpiente.",
        "stats": {"fuerza": 92, "magia": 68, "defensa": 89, "agilidad": 86},
        "special_move": "Zarpazo Titánico de la Jungla",
        "weapon_type": "claws_beast"
    },
    "trap jaw": {
        "canonical_name": "Trap Jaw",
        "faction": "Guerreros Diabólicos",
        "type_line": "Cíborg Legendario — Guerrero Diabólico",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "metal", "blaster"],
        "lore": "Cíborg mercenario letal con mandíbula de hierro capaz de triturar cualquier aleación del cosmos. Su brazo biomecánico intercambiable porta herramientas de aniquilación pura.",
        "stats": {"fuerza": 93, "magia": 62, "defensa": 95, "agilidad": 82},
        "special_move": "Mordisco de Mandíbula de Acero",
        "weapon_type": "mechanical_trap"
    },
    "tri-klops": {
        "canonical_name": "Tri-Klops",
        "faction": "Guerreros Diabólicos",
        "type_line": "Espadachín Táctico — Rastreador Diabólico",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "sword", "laser"],
        "lore": "Espadachín y rastreador supremo cuyo visor rotatorio le confiere visión nocturna, térmica y rayos gama destructivos. Un combatiente metódico y despiadado.",
        "stats": {"fuerza": 89, "magia": 70, "defensa": 87, "agilidad": 93},
        "special_move": "Láser Óptico de Rastreo Letal",
        "weapon_type": "mechanical_trap"
    },
    "evil-lyn": {
        "canonical_name": "Evil-Lyn",
        "faction": "Guerreros Diabólicos",
        "type_line": "Hechicera de las Sombras — Consejera Diabólica",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "havoc", "arcane"],
        "lore": "Hechicera de las sombras y maquiavélica consejera en la corte de Skeletor. Con su orbe de adivinación y conjuros arcanos dobla la realidad a su siniestra voluntad.",
        "stats": {"fuerza": 75, "magia": 97, "defensa": 80, "agilidad": 90},
        "special_move": "Tormenta Ilusoria de Subternia",
        "weapon_type": "magic_sorcery"
    },
    "mer-man": {
        "canonical_name": "Mer-Man",
        "faction": "Guerreros Diabólicos",
        "type_line": "Soberano Acuático — Señor de Rakash",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "water", "trident"],
        "lore": "Soberano indiscutible del reino acuático de Rakash y amo de los leviatanes submarinos. Con su tridente y control de las mareas arrastra a sus enemigos al abismo.",
        "stats": {"fuerza": 87, "magia": 85, "defensa": 86, "agilidad": 92},
        "special_move": "Tsunami de las Profundidades de Rakash",
        "weapon_type": "water_ocean"
    },
    "faker": {
        "canonical_name": "Faker",
        "faction": "Guerreros Diabólicos",
        "type_line": "Cíborg Impostor — Creación Diabólica",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "dark", "sword"],
        "lore": "Duplicado cibernético perverso de He-Man con piel azulada y circuitos fríos bajo el pecho. Creado para sembrar la confusión y destruir la esperanza en Eternia.",
        "stats": {"fuerza": 97, "magia": 76, "defensa": 94, "agilidad": 88},
        "special_move": "Tajo Cósmico de Luz Ancestral",
        "weapon_type": "power_sword"
    },
    "scare glow": {
        "canonical_name": "Scare Glow",
        "faction": "Guerreros Diabólicos",
        "type_line": "Espíritu Espectral — Heraldo del Pavor",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "havoc", "spectral"],
        "lore": "Fantasma esquelético refulgente que infunde un pavor paralizante en los corazones más valientes. Portando su guadaña de la muerte acecha en las noches de Eternia.",
        "stats": {"fuerza": 86, "magia": 96, "defensa": 84, "agilidad": 89},
        "special_move": "Juicio Espectral de Havoc",
        "weapon_type": "havoc_staff"
    },
    "clawful": {
        "canonical_name": "Clawful",
        "faction": "Guerreros Diabólicos",
        "type_line": "Criatura Legendaria — Bruto Acorazado",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "crustacean"],
        "lore": "Bruto acorazado con una pinza descomunal capaz de pulverizar rocas y escudos de Grayskull. Su caparazón impenetrable lo vuelve una pesadilla en combate frontal.",
        "stats": {"fuerza": 94, "magia": 50, "defensa": 97, "agilidad": 74},
        "special_move": "Presa Hidráulica Trituradora",
        "weapon_type": "mechanical_trap"
    },
    "whiplash": {
        "canonical_name": "Whiplash",
        "faction": "Guerreros Diabólicos",
        "type_line": "Criatura Legendaria — Reptil de Combate",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "reptile"],
        "lore": "Reptil de combate dotado de una cola masiva que azota con la potencia de un ariete. Su agilidad anfibia y piel escamosa lo convierten en un demoledor implacable.",
        "stats": {"fuerza": 91, "magia": 56, "defensa": 92, "agilidad": 88},
        "special_move": "Azote Ofídico Venenoso",
        "weapon_type": "snake_venom"
    },
    "webstor": {
        "canonical_name": "Webstor",
        "faction": "Guerreros Diabólicos",
        "type_line": "Criatura Legendaria — Maestro Arácnido",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "spider"],
        "lore": "Astuto infiltrador arácnido capaz de escalar cualquier fortaleza con su garfio de rescate y tejer trampas asfixiantes en las sombras de Subternia.",
        "stats": {"fuerza": 88, "magia": 74, "defensa": 89, "agilidad": 95},
        "special_move": "Presa Hidráulica Trituradora",
        "weapon_type": "mechanical_trap"
    },
    "spikor": {
        "canonical_name": "Spikor",
        "faction": "Guerreros Diabólicos",
        "type_line": "Criatura Legendaria — Herrero de Espinas",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "spikes"],
        "lore": "Herrero y guerrero cubierto de púas de acero impenetrables. Su mazo tridente y cuerpo espinado castigan a cualquiera que intente un ataque cuerpo a cuerpo.",
        "stats": {"fuerza": 92, "magia": 55, "defensa": 98, "agilidad": 76},
        "special_move": "Martillazo Sísmico de Titanio",
        "weapon_type": "ram_mace"
    },
    "stinkor": {
        "canonical_name": "Stinkor",
        "faction": "Guerreros Diabólicos",
        "type_line": "Criatura Legendaria — Maestro del Olor",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "toxin"],
        "lore": "Guerrero mutado capaz de liberar una nube de toxinas fétidas sofocantes que doblega a batallones enteros antes de que puedan desenfundar sus espadas.",
        "stats": {"fuerza": 85, "magia": 68, "defensa": 88, "agilidad": 84},
        "special_move": "Chorro Ácido Corrosivo",
        "weapon_type": "snake_venom"
    },
    "two-bad": {
        "canonical_name": "Two-Bad",
        "faction": "Guerreros Diabólicos",
        "type_line": "Criatura Legendaria — Estratega Bicéfalo",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "chaos"],
        "lore": "Guerrero bicéfalo fusionado que combina la fuerza bruta con la astucia traicionera. Aunque sus dos cabezas discuten, sus ataques dobles son devastadores.",
        "stats": {"fuerza": 93, "magia": 58, "defensa": 91, "agilidad": 80},
        "special_move": "Hendidura Doble de Acero Eterniano",
        "weapon_type": "battle_axe"
    },

    # ── LA HORDA DEL TERROR (THE EVIL HORDE) ──
    "hordak": {
        "canonical_name": "Hordak",
        "faction": "La Horda del Terror",
        "type_line": "Tirano Supremo — Líder de la Horda",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "horde", "plasma", "dark"],
        "lore": "Tirano supremo de la Zona del Terror y maestro de la tecno-magia oscura. Capaz de transmutar su propio cuerpo en armamento mecánico para subyugar mundos enteros.",
        "stats": {"fuerza": 95, "magia": 96, "defensa": 95, "agilidad": 87},
        "special_move": "Flecha de Plasma Carmesí de la Horda",
        "weapon_type": "horde_crossbow"
    },
    "shadow weaver": {
        "canonical_name": "Shadow Weaver",
        "faction": "La Horda del Terror",
        "type_line": "Hechicera Oscura — Bruja de la Horda",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "horde", "arcane"],
        "lore": "Poderosa maga oscura oculta tras su velo carmesí. Canaliza los misterios prohibidos de Mystacor para servir a la tiranía imperial de Hordak.",
        "stats": {"fuerza": 70, "magia": 99, "defensa": 82, "agilidad": 88},
        "special_move": "Invocación del Velo Demoníaco",
        "weapon_type": "magic_sorcery"
    },
    "catra": {
        "canonical_name": "Catra",
        "faction": "La Horda del Terror",
        "type_line": "Capitana de la Fuerza — Máscara Felina",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "feline", "agility"],
        "lore": "Capitana de la Fuerza de la Horda dotada de una máscara mágica que le otorga la forma y ferocidad de una pantera asesina. Rival incansable de She-Ra.",
        "stats": {"fuerza": 88, "magia": 84, "defensa": 85, "agilidad": 98},
        "special_move": "Zarpazo Titánico de la Jungla",
        "weapon_type": "claws_beast"
    },
    "grizzlor": {
        "canonical_name": "Grizzlor",
        "faction": "La Horda del Terror",
        "type_line": "Bestia Salvaje — Bruto de la Horda",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "beast"],
        "lore": "Monstruo peludo legendario con garras devastadoras y una furia incontenible. Un arma viviente de terror enviada por Hordak para aplastar la rebelión.",
        "stats": {"fuerza": 95, "magia": 52, "defensa": 94, "agilidad": 80},
        "special_move": "Desgarro Feroz de la Selva Carmesí",
        "weapon_type": "claws_beast"
    },
    "mantenna": {
        "canonical_name": "Mantenna",
        "faction": "La Horda del Terror",
        "type_line": "Vigía de Asalto — Ojos Láser de la Horda",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "laser"],
        "lore": "Espía de cuatro piernas con ojos telescópicos capaces de disparar rayos aturdidores y desintegradores. Vigila las fronteras de la Zona del Terror.",
        "stats": {"fuerza": 84, "magia": 72, "defensa": 86, "agilidad": 91},
        "special_move": "Láser Óptico de Rastreo Letal",
        "weapon_type": "laser_blaster"
    },
    "leech": {
        "canonical_name": "Leech",
        "faction": "La Horda del Terror",
        "type_line": "Drenador Vital — Anfibio de la Horda",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "drain"],
        "lore": "Criatura anfibia con ventosas descomunales capaces de absorber la energía vital y mágica de sus oponentes, dejándolos exhaustos en segundos.",
        "stats": {"fuerza": 93, "magia": 80, "defensa": 92, "agilidad": 75},
        "special_move": "Saeta Vampírica de Hordak",
        "weapon_type": "horde_crossbow"
    },
    "mosquitor": {
        "canonical_name": "Mosquitor",
        "faction": "La Horda del Terror",
        "type_line": "Drenador de Energía — Soldado Sangriento",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "blood"],
        "lore": "Cíborg insectoide con una trompa de extracción capaz de bombear la energía y fluidos vitales de sus víctimas directamente a su pecho blindado.",
        "stats": {"fuerza": 90, "magia": 70, "defensa": 93, "agilidad": 88},
        "special_move": "Saeta Vampírica de Hordak",
        "weapon_type": "horde_crossbow"
    },

    # ── LOS HOMBRES SERPIENTE (THE SNAKE MEN) ──
    "king hiss": {
        "canonical_name": "King Hiss",
        "faction": "Los Hombres Serpiente",
        "type_line": "Monarca Ofídico — Líder de los Hombres Serpiente",
        "frame_theme": "snake_men",
        "emblem": "snake",
        "mana_gems": ["snake", "snake", "poison", "ancient"],
        "lore": "Antiquísimo monarca ofídico cuyo disfraz humano oculta una masa de serpientes devoradoras. Regresa de las sombras del pasado para reclamar el dominio de Eternia.",
        "stats": {"fuerza": 93, "magia": 95, "defensa": 91, "agilidad": 93},
        "special_move": "Mordisco Asfixiante del Rey Hiss",
        "weapon_type": "snake_venom"
    },
    "kobra khan": {
        "canonical_name": "Kobra Khan",
        "faction": "Los Hombres Serpiente",
        "type_line": "Guerrillero Reptiliano — Emisario de Veneno",
        "frame_theme": "snake_men",
        "emblem": "snake",
        "mana_gems": ["snake", "acid"],
        "lore": "Guerrillero reptiliano capaz de expulsar una niebla soporífera y ácido mortal desde su garganta. Un emboscador maestro de las marismas eternianas.",
        "stats": {"fuerza": 84, "magia": 78, "defensa": 85, "agilidad": 91},
        "special_move": "Chorro Ácido Corrosivo",
        "weapon_type": "snake_venom"
    },
    "rattlor": {
        "canonical_name": "Rattlor",
        "faction": "Los Hombres Serpiente",
        "type_line": "Guerrero Cascabel — Vanguardia Ofidia",
        "frame_theme": "snake_men",
        "emblem": "snake",
        "mana_gems": ["snake", "strike"],
        "lore": "Vanguardia de los Hombres Serpiente con cuello telescópico de impacto y un cascabel sónico que paraliza a sus presas antes del golpe definitivo.",
        "stats": {"fuerza": 91, "magia": 65, "defensa": 90, "agilidad": 92},
        "special_move": "Azote Ofídico Venenoso",
        "weapon_type": "snake_venom"
    },
    "tung lashr": {
        "canonical_name": "Tung Lashr",
        "faction": "Los Hombres Serpiente",
        "type_line": "Emboscador Ofídico — Lengua Venenosa",
        "frame_theme": "snake_men",
        "emblem": "snake",
        "mana_gems": ["snake", "venom"],
        "lore": "Infiltrador reptil con una lengua retráctil impregnada de toxinas paralizantes. Puede desarmar a los guerreros más diestros a metros de distancia.",
        "stats": {"fuerza": 86, "magia": 70, "defensa": 87, "agilidad": 94},
        "special_move": "Azote Ofídico Venenoso",
        "weapon_type": "snake_venom"
    },
    "snake face": {
        "canonical_name": "Snake Face",
        "faction": "Los Hombres Serpiente",
        "type_line": "Petrificador Ancestral — Ojos de Serpiente",
        "frame_theme": "snake_men",
        "emblem": "snake",
        "mana_gems": ["snake", "petrify"],
        "lore": "Terrorífico guerrero de cuyo rostro y pecho brotan víboras que petrifican en piedra sólida a cualquiera que ose cruzar su mirada.",
        "stats": {"fuerza": 89, "magia": 94, "defensa": 93, "agilidad": 82},
        "special_move": "Hipnosis de la Serpiente Carmesí",
        "weapon_type": "snake_venom"
    },
    "sssqueeze": {
        "canonical_name": "Sssqueeze",
        "faction": "Los Hombres Serpiente",
        "type_line": "Estrangulador de Grayskull — Brazos Ofidios",
        "frame_theme": "snake_men",
        "emblem": "snake",
        "mana_gems": ["snake", "constrict"],
        "lore": "Guerrero con brazos serpenteantes extensibles capaces de asfixiar y triturar vehículos de asedio con una fuerza de constricción titánica.",
        "stats": {"fuerza": 94, "magia": 62, "defensa": 90, "agilidad": 89},
        "special_move": "Estrangulamiento de Pitón Arcano",
        "weapon_type": "snake_venom"
    },

    # ── LA GRAN REBELIÓN (THE GREAT REBELLION) ──
    "she-ra": {
        "canonical_name": "She-Ra",
        "faction": "La Gran Rebelión",
        "type_line": "Princesa del Poder — Campeona de Etheria",
        "frame_theme": "great_rebellion",
        "emblem": "sparkles",
        "mana_gems": ["rebellion", "rebellion", "crystal", "sword"],
        "lore": "Princesa del Poder y líder invicta de la Gran Rebelión en Etheria. Con la Espada de Protección canaliza la luz pura del honor y la libertad.",
        "stats": {"fuerza": 98, "magia": 94, "defensa": 95, "agilidad": 96},
        "special_move": "Tajo Cósmico de Luz Ancestral",
        "weapon_type": "power_sword"
    },
    "bow": {
        "canonical_name": "Bow",
        "faction": "La Gran Rebelión",
        "type_line": "Arquero Rebelde — Corazón Valiente",
        "frame_theme": "great_rebellion",
        "emblem": "sparkles",
        "mana_gems": ["rebellion", "arrow"],
        "lore": "Tirador legendario y alma noble de la rebelión. Sus flechas mágicas especiales desarman las defensas de la Horda con precisión quirúrgica.",
        "stats": {"fuerza": 85, "magia": 76, "defensa": 82, "agilidad": 95},
        "special_move": "Dardo Perforador de Etheria",
        "weapon_type": "laser_blaster"
    },
    "glimmer": {
        "canonical_name": "Glimmer",
        "faction": "La Gran Rebelión",
        "type_line": "Princesa de Bright Moon — Luz de Etheria",
        "frame_theme": "great_rebellion",
        "emblem": "sparkles",
        "mana_gems": ["rebellion", "light"],
        "lore": "Heredera de Bright Moon con el poder de proyectar destellos de luz cegadora y teletransportarse a través del campo de batalla.",
        "stats": {"fuerza": 75, "magia": 92, "defensa": 80, "agilidad": 90},
        "special_move": "Lanza de Luz Arcana de Zoar",
        "weapon_type": "magic_sorcery"
    },

    # ── GUARDIANES CÓSMICOS & MULTIVERSO ──
    "zodac": {
        "canonical_name": "Zodac",
        "faction": "Guardianes Cósmicos",
        "type_line": "Ejecutor Cósmico — Juez del Equilibrio",
        "frame_theme": "cosmic_enforcers",
        "emblem": "infinity",
        "mana_gems": ["cosmic", "cosmic", "neutral", "star"],
        "lore": "Enforcer Cósmico neutral que vela por el equilibrio universal entre la luz y las sombras. Con su silla flotante y conocimiento infinito interviene solo cuando el destino pende de un hilo.",
        "stats": {"fuerza": 90, "magia": 95, "defensa": 92, "agilidad": 91},
        "special_move": "Descarga Cósmica de Zodac",
        "weapon_type": "cosmic_flight"
    },
    "zodak": {
        "canonical_name": "Zodak",
        "faction": "Guardianes Cósmicos",
        "type_line": "Ejecutor Cósmico — Cazador de Serpientes",
        "frame_theme": "cosmic_enforcers",
        "emblem": "infinity",
        "mana_gems": ["cosmic", "cosmic", "strike"],
        "lore": "Guardián inmortal bendecido con artes marciales celestiales y un juramento sagrado de erradicar la amenaza de los Hombres Serpiente.",
        "stats": {"fuerza": 93, "magia": 92, "defensa": 91, "agilidad": 95},
        "special_move": "Descarga Cósmica de Zodac",
        "weapon_type": "cosmic_flight"
    },
    "he-ro": {
        "canonical_name": "He-Ro",
        "faction": "Guardianes Cósmicos",
        "type_line": "Mago Cósmico Supremo — Ancestro de Grayskull",
        "frame_theme": "cosmic_enforcers",
        "emblem": "infinity",
        "mana_gems": ["cosmic", "arcane", "gold", "staff"],
        "lore": "El Hechicero Supremo de Preternia cuyo báculo glorioso canaliza los misterios de la creación para legar el poder a las futuras generaciones de héroes.",
        "stats": {"fuerza": 92, "magia": 99, "defensa": 94, "agilidad": 90},
        "special_move": "Tajo Cósmico de Luz Ancestral",
        "weapon_type": "magic_sorcery"
    },
    "king grayskull": {
        "canonical_name": "King Grayskull",
        "faction": "Guerreros Heroicos",
        "type_line": "Rey Ancestral — Fundador de Grayskull",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "grayskull", "power", "sword"],
        "lore": "Monarca legendario de la antigüedad que sacrificó su vida para bendecir la espada del poder y sellar las almenas de la fortaleza sagrada de Grayskull.",
        "stats": {"fuerza": 99, "magia": 95, "defensa": 97, "agilidad": 89},
        "special_move": "Furia del Relámpago de Grayskull",
        "weapon_type": "power_sword"
    },
    "lion-o": {
        "canonical_name": "Lion-O",
        "faction": "Alianzas del Multiverso",
        "type_line": "Criatura Legendaria — Señor de Thundera",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["thundera", "thundera", "sword"],
        "lore": "Señor noble de los Thundercats y portador de la legendaria Espada del Augurio. En su alianza mística con Grayskull, canaliza el Ojo de Thundera contra la oscuridad cósmica.",
        "stats": {"fuerza": 96, "magia": 92, "defensa": 93, "agilidad": 97},
        "special_move": "Furia del Ojo de Thundera",
        "weapon_type": "sword_of_omens"
    },
    "mumm-ra": {
        "canonical_name": "Mumm-Ra el Inmortal",
        "faction": "Alianzas del Multiverso",
        "type_line": "Sacerdote Maldito — Siervo de los Antiguos",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "havoc", "ancient"],
        "lore": "Sacerdote milenario y conducto de los Antiguos Espíritus del Mal. Al transformarse en su forma imperecedera, desata una catástrofe de poder destructivo.",
        "stats": {"fuerza": 96, "magia": 99, "defensa": 94, "agilidad": 86},
        "special_move": "Descarga de Sombras Arcanas",
        "weapon_type": "havoc_staff"
    },
    "dragstor": {
        "canonical_name": "Dragstor",
        "faction": "La Horda del Terror",
        "type_line": "Cíborg de Asalto — Soldado de la Horda",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "horde", "speed"],
        "lore": "Cíborg de combate veloz como el rayo impulsado por la turbina de su pecho. Es el bólido de persecución y choque más letal de la Zona del Terror.",
        "stats": {"fuerza": 91, "magia": 75, "defensa": 93, "agilidad": 98},
        "special_move": "Aceleración Sónica de la Rueda Cibernética",
        "weapon_type": "horde_crossbow"
    },
    "multi-bot": {
        "canonical_name": "Multi-Bot",
        "faction": "La Horda del Terror",
        "type_line": "Ingenio Mecánico — Soldado de la Horda",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "horde", "plasma"],
        "lore": "Robot multi-modular creado en los laboratorios de Modulok. Es capaz de dividirse, recombinar sus diez extremidades y disparar desde ángulos imposibles.",
        "stats": {"fuerza": 92, "magia": 78, "defensa": 94, "agilidad": 88},
        "special_move": "Modulación de Diez Extremidades Letales",
        "weapon_type": "laser_blaster"
    },
    "rokkon": {
        "canonical_name": "Rokkon",
        "faction": "Guerreros Heroicos",
        "type_line": "Guerrero Roca — Defensor de Eternia",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "stone", "defense"],
        "lore": "Valeroso guerrero del Pueblo de Roca. Su coraza meteórica le permite transformarse en una roca impenetrable capaz de repeler cualquier impacto energético.",
        "stats": {"fuerza": 90, "magia": 75, "defensa": 99, "agilidad": 82},
        "special_move": "Coraza de Meteorito Impenetrable",
        "weapon_type": "laser_blaster"
    },
    "stonedar": {
        "canonical_name": "Stonedar",
        "faction": "Guerreros Heroicos",
        "type_line": "Líder de los Hombres Roca — Defensor de Eternia",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "stone", "gold"],
        "lore": "Sabio y solemne líder de los Hombres de Roca. Su armadura de roca viva repele cualquier rayo láser devolviendo la energía concentrada hacia sus atacantes.",
        "stats": {"fuerza": 93, "magia": 82, "defensa": 99, "agilidad": 84},
        "special_move": "Transformación de Fortaleza Pétrea",
        "weapon_type": "laser_blaster"
    },
    "gwildor": {
        "canonical_name": "Gwildor",
        "faction": "Guerreros Heroicos",
        "type_line": "Inventor Thenuriano — Guardián Dimensional",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "cosmic", "tech"],
        "lore": "Genio inventor Thenuriano y creador de la Llave Cósmica. Mediante frecuencias de sonido místicas puede abrir portales a cualquier confín del tiempo y el espacio.",
        "stats": {"fuerza": 78, "magia": 96, "defensa": 85, "agilidad": 86},
        "special_move": "Sintonización Armónica de la Llave Cósmica",
        "weapon_type": "magic_sorcery"
    },
    "king grayskull": {
        "canonical_name": "King Grayskull",
        "faction": "Guerreros Heroicos",
        "type_line": "Rey Ancestral — Campeón Primigenio",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "grayskull", "gold", "sword"],
        "lore": "Monarca legendario de la antigua Eternia que entregó su espíritu para sellar a Hordak. De su linaje y coraje brota la fuente original del Poder de Grayskull.",
        "stats": {"fuerza": 99, "magia": 97, "defensa": 98, "agilidad": 94},
        "special_move": "Poder Primigenio de Grayskull",
        "weapon_type": "power_sword"
    },
    "lord gr'asp": {
        "canonical_name": "Lord Gr'Asp",
        "faction": "Los Hombres Serpiente",
        "type_line": "Estratega Ofídico — Hombre Serpiente",
        "frame_theme": "snake_men",
        "emblem": "snake",
        "mana_gems": ["snake", "snake", "venom"],
        "lore": "General y maestro estratega de los Hombres Serpiente. Dotado de una monstruosa pinza trituradora y mente maquiavélica para orquestar emboscadas。",
        "stats": {"fuerza": 93, "magia": 88, "defensa": 94, "agilidad": 90},
        "special_move": "Apresamiento Asfixiante de Tenaza",
        "weapon_type": "mechanical_trap"
    },
    "frog monger": {
        "canonical_name": "Frog Monger",
        "faction": "Guerreros Diabólicos",
        "type_line": "Monstruo de las Mazmorras — Bestia Diabólica",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "beast", "acid"],
        "lore": "Mutante anfibio fugado de los calabozos subterráneos del Castillo Grayskull. Dispara fluidos corrosivos y salta con agilidad salvaje sobre sus presas.",
        "stats": {"fuerza": 88, "magia": 76, "defensa": 89, "agilidad": 95},
        "special_move": "Salto Ácido de las Mazmorras",
        "weapon_type": "laser_blaster"
    },
    "castaspella": {
        "canonical_name": "Castaspella",
        "faction": "La Gran Rebelión",
        "type_line": "Gran Hechicera — Gran Rebelión",
        "frame_theme": "great_rebellion",
        "emblem": "sparkles",
        "mana_gems": ["rebellion", "crystal", "magic"],
        "lore": "Reina de Mystacor y aliada fundamental de She-Ra. Domina los vórtices hipnóticos y la magia arcana de luz para desconcertar a los ejércitos de la Horda.",
        "stats": {"fuerza": 84, "magia": 97, "defensa": 88, "agilidad": 91},
        "special_move": "Danza Ilusoria de Mystacor",
        "weapon_type": "magic_sorcery"
    },
    "frosta": {
        "canonical_name": "Frosta",
        "faction": "La Gran Rebelión",
        "type_line": "Reina del Hielo — Gran Rebelión",
        "frame_theme": "great_rebellion",
        "emblem": "sparkles",
        "mana_gems": ["rebellion", "ice", "crystal"],
        "lore": "Soberana del Reino de las Nieves de Etheria. Canaliza el cero absoluto para erigir murallas gélidas y congelar la maquinaria pesada de Hordak.",
        "stats": {"fuerza": 86, "magia": 96, "defensa": 92, "agilidad": 92},
        "special_move": "Ventisca Glacial de Castle Chill",
        "weapon_type": "magic_sorcery"
    },
    "netossa": {
        "canonical_name": "Netossa",
        "faction": "La Gran Rebelión",
        "type_line": "Cazadora Táctica — Gran Rebelión",
        "frame_theme": "great_rebellion",
        "emblem": "sparkles",
        "mana_gems": ["rebellion", "light", "energy"],
        "lore": "Maestra de la táctica armada con su red mística de energía indestructible. Es capaz de atrapar batallones enteros de la Horda con precisión quirúrgica.",
        "stats": {"fuerza": 89, "magia": 90, "defensa": 91, "agilidad": 96},
        "special_move": "Red de Energía Prismática",
        "weapon_type": "mechanical_trap"
    },
    "kowl": {
        "canonical_name": "Kowl",
        "faction": "La Gran Rebelión",
        "type_line": "Consejero Alado — Guardián de Etheria",
        "frame_theme": "great_rebellion",
        "emblem": "sparkles",
        "mana_gems": ["rebellion", "wind"],
        "lore": "Noble criatura alada dotada de aguda inteligencia y fiel compañero de Bow y She-Ra. Con sus grandes orejas vuela y presiente el peligro a gran distancia.",
        "stats": {"fuerza": 65, "magia": 92, "defensa": 80, "agilidad": 98},
        "special_move": "Vuelo de Alerta e Intuición Mística",
        "weapon_type": "magic_sorcery"
    },
    "swift wind": {
        "canonical_name": "Swift Wind",
        "faction": "La Gran Rebelión",
        "type_line": "Corcel Celestial — Campeón de Etheria",
        "frame_theme": "great_rebellion",
        "emblem": "sparkles",
        "mana_gems": ["rebellion", "crystal", "sword"],
        "lore": "El noble corcel alado de She-Ra, transformado por la Espada de Protección. Con su cuerno de unicornio y alas prismáticas surca los cielos a la velocidad de la luz.",
        "stats": {"fuerza": 97, "magia": 95, "defensa": 96, "agilidad": 99},
        "special_move": "Embestida Cósmica del Unicornio Alado",
        "weapon_type": "magic_sorcery"
    },
    "arrow": {
        "canonical_name": "Arrow",
        "faction": "La Gran Rebelión",
        "type_line": "Corcel Alado — Montura de Bow",
        "frame_theme": "great_rebellion",
        "emblem": "sparkles",
        "mana_gems": ["rebellion", "wind"],
        "lore": "Fiel corcel de Bow de pelaje azul y alas resplandecientes. Capaz de galopar por los vientos de Etheria transportando a los campeones de la Gran Rebelión.",
        "stats": {"fuerza": 91, "magia": 86, "defensa": 92, "agilidad": 97},
        "special_move": "Galope Veloz con Alas de Luz",
        "weapon_type": "magic_sorcery"
    },
    "fright zone": {
        "canonical_name": "The Fright Zone",
        "faction": "La Horda del Terror",
        "type_line": "Fortaleza Tenebrosa — Bastión de la Horda",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "horde", "plasma", "dark"],
        "lore": "La tétrica base de operaciones de Hordak en Etheria. Protegida por trampas biomecánicas, emanaciones tóxicas y el temible árbol carnívoro carmesí.",
        "stats": {"fuerza": 99, "magia": 97, "defensa": 99, "agilidad": 70},
        "special_move": "Trampa Asfixiante del Árbol Devorador",
        "weapon_type": "horde_crossbow"
    },
    "mantisaur": {
        "canonical_name": "Mantisaur",
        "faction": "La Horda del Terror",
        "type_line": "Insectoide Gigante — Montura de Hordak",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "beast", "plasma"],
        "lore": "Monstruoso insecto cibernético de combate que sirve de montura a Hordak. Sus pinzas afiladas trituran vehículos acorazados en milésimas de segundo.",
        "stats": {"fuerza": 95, "magia": 88, "defensa": 94, "agilidad": 93},
        "special_move": "Tenaza Cortante de la Mantis Gigante",
        "weapon_type": "mechanical_trap"
    },
    "stridor": {
        "canonical_name": "Stridor",
        "faction": "Guerreros Heroicos",
        "type_line": "Corcel Mecánico — Artillería Blindada",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "tech", "gold"],
        "lore": "Caballo de guerra robótico blindado diseñado por Man-At-Arms. Equipado con cañones láser dobles y casco de titanio para romper formaciones enemigas.",
        "stats": {"fuerza": 96, "magia": 80, "defensa": 98, "agilidad": 90},
        "special_move": "Cañonazo Láser de la Montura Blindada",
        "weapon_type": "laser_blaster"
    },
    "bionatops": {
        "canonical_name": "Bionatops",
        "faction": "Guerreros Heroicos",
        "type_line": "Dinosaurio Biónico — Bestia de la Prehistoria",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "beast", "tech"],
        "lore": "Triceratops biónico de la Prehistoria de Eternia. Su coraza reforzada y triple cuerno electrocargado lo convierten en un ariete viviente imparable.",
        "stats": {"fuerza": 98, "magia": 82, "defensa": 99, "agilidad": 80},
        "special_move": "Carga de Cuerno Cibernético Perforante",
        "weapon_type": "ram_mace"
    },
    "turbodactyl": {
        "canonical_name": "Turbodactyl",
        "faction": "Guerreros Heroicos",
        "type_line": "Pterodáctilo Biónico — Guardián Aéreo",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "beast", "speed"],
        "lore": "Pterodáctilo cibernético prehistórico capaz de vuelos supersónicos y bombardeos energéticos de precisión sobre las legiones de la Horda y los Snake Men.",
        "stats": {"fuerza": 92, "magia": 80, "defensa": 94, "agilidad": 99},
        "special_move": "Vuelo Supersónico con Rastreo Térmico",
        "weapon_type": "laser_blaster"
    },
    "tyrantisaurus rex": {
        "canonical_name": "Tyrantisaurus Rex",
        "faction": "Guerreros Diabólicos",
        "type_line": "Tiranosaurio Biónico — Monstruo Titánico",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "beast", "destruction"],
        "lore": "El depredador definitivo de la prehistoria eterniana al servicio de Skeletor. Con cañones dorsales y mandíbulas de titanio devora fortificaciones enteras.",
        "stats": {"fuerza": 99, "magia": 86, "defensa": 97, "agilidad": 85},
        "special_move": "Mordisco Triturador Dinámico",
        "weapon_type": "claws_beast"
    },
    "tytus": {
        "canonical_name": "Tytus",
        "faction": "Guerreros Heroicos",
        "type_line": "Titán Heroico — Gigante de la Antigüedad",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "gold", "earth"],
        "lore": "Titán bondadoso de la era precataclísmica que luchó hombro con hombro junto al Rey Grayskull. Su colosal tamaño y arma de captura aplastan a cualquier invasor.",
        "stats": {"fuerza": 100, "magia": 90, "defensa": 99, "agilidad": 84},
        "special_move": "Pisotón Sísmico de Gigante",
        "weapon_type": "ram_mace"
    },
    "megator": {
        "canonical_name": "Megator",
        "faction": "Guerreros Diabólicos",
        "type_line": "Titán Monstruoso — Gigante del Caos",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "blood", "earth"],
        "lore": "El gigante más sanguinario de las fuerzas de la oscuridad. Aliado de los Hombres Serpiente, blande una maza con púas capaz de desmoronar montañas.",
        "stats": {"fuerza": 100, "magia": 89, "defensa": 98, "agilidad": 82},
        "special_move": "Maza Aplastante de las Sombras",
        "weapon_type": "ram_mace"
    },
    "mouse-jaw": {
        "canonical_name": "Mouse-Jaw",
        "faction": "Guerreros Diabólicos",
        "type_line": "Mutación Mecánica — Guerrero Diabólico",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "tech", "mutagen"],
        "lore": "Cíborg nacido de la unión del arsenal de Trap Jaw con la tecnología biomecánica de los Mousers. Sus mandíbulas mecánicas cortan cualquier aleación.",
        "stats": {"fuerza": 93, "magia": 78, "defensa": 95, "agilidad": 89},
        "special_move": "Mordaza Cazarratones Trituradora",
        "weapon_type": "mechanical_trap"
    },
    "randy savage": {
        "canonical_name": '"Macho Man" Randy Savage',
        "faction": "Alianzas del Multiverso",
        "type_line": "Campeón Legendario — Leyenda del Ring",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "gold", "energy"],
        "lore": "El inigualable Macho Man revestido de armadura de combate de Grayskull. Desciende desde las alturas de Eternia con su fulminante codazo volador.",
        "stats": {"fuerza": 95, "magia": 86, "defensa": 92, "agilidad": 96},
        "special_move": "Codazo Volador Cósmico",
        "weapon_type": "power_sword"
    },
    "bret hart": {
        "canonical_name": 'Bret "Hit Man" Hart',
        "faction": "Alianzas del Multiverso",
        "type_line": "Maestro Técnico — Alianza del Multiverso",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "crystal", "energy"],
        "lore": "Lo mejor que hay, lo mejor que hubo y lo mejor que habrá. Protegido con armadura fotónica de Eternia, somete a cualquier rival con su Sharpshooter.",
        "stats": {"fuerza": 93, "magia": 85, "defensa": 93, "agilidad": 95},
        "special_move": "Francotirador del Sharpshooter",
        "weapon_type": "power_sword"
    },
    "kane": {
        "canonical_name": "Kane",
        "faction": "Alianzas del Multiverso",
        "type_line": "Monstruo Rojo — Alianza de las Sombras",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "blood", "fire"],
        "lore": "El Monstruo Rojo emerge de las profundidades volcánicas de Snake Mountain canalizando llamas arcanas y ejecutando su Chokeslam devastador.",
        "stats": {"fuerza": 97, "magia": 90, "defensa": 96, "agilidad": 88},
        "special_move": "Chokeslam del Fuego Infernal",
        "weapon_type": "havoc_staff"
    },
    "rey mysterio": {
        "canonical_name": "Rey Mysterio",
        "faction": "Alianzas del Multiverso",
        "type_line": "Luchador Aéreo — Defensor del Cosmos",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "wind", "speed"],
        "lore": "Maestro indiscutible del combate aéreo y la agilidad mística. Con sus alas de Grayskull ejecuta el 619 dejando sin respuesta a los gigantes del mal.",
        "stats": {"fuerza": 88, "magia": 91, "defensa": 89, "agilidad": 100},
        "special_move": "Vuelo 619 de la Nebulosa",
        "weapon_type": "power_sword"
    },
    "ultimate warrior": {
        "canonical_name": "Ultimate Warrior",
        "faction": "Alianzas del Multiverso",
        "type_line": "Guerrero Místico — Espíritu Inmortal",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "gold", "ancient"],
        "lore": "Canalizando los espíritus arcanos de Parts Unknown y el poder cósmico de Grayskull, sacude la realidad con su energía y plancha demoledora.",
        "stats": {"fuerza": 98, "magia": 95, "defensa": 96, "agilidad": 95},
        "special_move": "Plancha de los Dioses Guerreros",
        "weapon_type": "power_sword"
    },
    "hit man": {
        "canonical_name": 'Bret "Hit Man" Hart',
        "faction": "Alianzas del Multiverso",
        "type_line": "Maestro Técnico — Alianza del Multiverso",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "crystal", "energy"],
        "lore": "Lo mejor que hay, lo mejor que hubo y lo mejor que habrá. Protegido con armadura fotónica de Eternia, somete a cualquier rival con su Sharpshooter.",
        "stats": {"fuerza": 93, "magia": 85, "defensa": 93, "agilidad": 95},
        "special_move": "Francotirador del Sharpshooter",
        "weapon_type": "power_sword"
    },
    "digitino": {
        "canonical_name": "Digitino",
        "faction": "Guerreros Heroicos",
        "type_line": "Cerebro Cibernético — Guerrero Heroico",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "tech", "gold"],
        "lore": "Computadora viviente aliada de los Guerreros Heroicos. Capaz de calcular en nanosegundos la trayectoria de cualquier proyectil y desmantelar defensas mecánicas enemigas.",
        "stats": {"fuerza": 85, "magia": 88, "defensa": 95, "agilidad": 90},
        "special_move": "Procesamiento Cuántico de Combate",
        "weapon_type": "laser_blaster"
    },
    "expand-or": {
        "canonical_name": "Expand-Or",
        "faction": "Guerreros Heroicos",
        "type_line": "Defensor Telescópico — Guerrero Heroico",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "defense", "gold"],
        "lore": "Guerrero dotado de placas telescópicas de expansión que multiplican su envergadura blindada, convirtiéndolo en un escudo móvil infranqueable.",
        "stats": {"fuerza": 92, "magia": 76, "defensa": 99, "agilidad": 84},
        "special_move": "Despliegue de Blindaje Telescópico",
        "weapon_type": "ram_mace"
    },
    "gray": {
        "canonical_name": "Gray",
        "faction": "Guardianes Cósmicos",
        "type_line": "Joven Chamán — Heredero de la Luz",
        "frame_theme": "cosmic_enforcers",
        "emblem": "infinity",
        "mana_gems": ["cosmic", "arcane", "light"],
        "lore": "Joven aprendiz dotado de magia primordial que en los albores de Preternia canaliza el poder de los Antiguos para transformarse en el legendario He-Ro.",
        "stats": {"fuerza": 86, "magia": 97, "defensa": 89, "agilidad": 93},
        "special_move": "Transmutación Arcana de He-Ro",
        "weapon_type": "magic_sorcery"
    },
    "grayskull mania": {
        "canonical_name": "Grayskull Mania Arena",
        "faction": "Alianzas del Multiverso",
        "type_line": "Cuadrilátero Sagrado — Arena de Grayskull",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "gold", "energy"],
        "lore": "El ring sagrado de combate donde los campeones de Eternia y los titanes del multiverso dirimen el destino del campeonato cósmico.",
        "stats": {"fuerza": 99, "magia": 90, "defensa": 99, "agilidad": 85},
        "special_move": "Choque en el Cuadrilátero del Destino",
        "weapon_type": "power_sword"
    },
    "meteorb": {
        "canonical_name": "Meteorbs",
        "faction": "Guerreros Heroicos",
        "type_line": "Criatura Meteórica — Aliado de Eternia",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "stone", "space"],
        "lore": "Criaturas nacidas de cometas mágicos que pueden rodar a gran velocidad como esferas y desplegarse en bestias de combate sorprendiendo al enemigo.",
        "stats": {"fuerza": 88, "magia": 82, "defensa": 94, "agilidad": 96},
        "special_move": "Despliegue Meteórico Sorpresa",
        "weapon_type": "ram_mace"
    },
    "raphael": {
        "canonical_name": "Raphael",
        "faction": "Alianzas del Multiverso",
        "type_line": "Ninja Feroz — Tortuga de Grayskull",
        "frame_theme": "castle_grayskull",
        "emblem": "shield",
        "mana_gems": ["grayskull", "turtle", "strike"],
        "lore": "El ninja más impulsivo y temible del Clan Hamato. Revestido con armadura de combate eterniana y sus sais gemelos, lidera la carga frontal.",
        "stats": {"fuerza": 94, "magia": 78, "defensa": 93, "agilidad": 96},
        "special_move": "Doble Estocada Sai de Grayskull",
        "weapon_type": "power_sword"
    },
    "storm": {
        "canonical_name": "Storm",
        "faction": "La Horda del Terror",
        "type_line": "Corcel de Guerra — Montura de la Horda",
        "frame_theme": "evil_horde",
        "emblem": "bat",
        "mana_gems": ["horde", "horde", "dark"],
        "lore": "El siniestro caballo de combate de Catra. Cabalga entre las nieblas de la Zona del Terror con garras afiladas y ferocidad salvaje.",
        "stats": {"fuerza": 92, "magia": 85, "defensa": 93, "agilidad": 97},
        "special_move": "Galope del Trueno Sombrío",
        "weapon_type": "horde_crossbow"
    },
    "shredder": {
        "canonical_name": "Shredder / Skele-Shredder",
        "faction": "Alianzas del Multiverso",
        "type_line": "Señor del Clan del Pie — Tirano Mutado",
        "frame_theme": "snake_mountain",
        "emblem": "skull",
        "mana_gems": ["havoc", "mutagen", "blade"],
        "lore": "Líder supremo del Clan del Pie fusionado con la magia oscura de Skeletor y el mutágeno. Sus cuchillas de acero emanan energía destructiva.",
        "stats": {"fuerza": 96, "magia": 92, "defensa": 95, "agilidad": 96},
        "special_move": "Corte de Acero Mutágeno del Pie",
        "weapon_type": "power_sword"
    }
}

def resolve_motu_profile(product_name: str, sub_category: Optional[str] = "MOTU Origins") -> Dict[str, Any]:
    """
    Resuelve el perfil canónico exacto de forma determinista para cualquier figura.
    """
    clean_name = product_name.lower().strip()
    sub_cat = sub_category or "MOTU Origins"

    # 1. Búsqueda exacta y por inclusión en la enciclopedia
    for key, data in MOTU_LORE_ENCYCLOPEDIA.items():
        if key in clean_name:
            return {
                "canonical_name": data["canonical_name"],
                "faction": data["faction"],
                "type_line": data["type_line"],
                "frame_theme": data["frame_theme"],
                "emblem": data["emblem"],
                "mana_gems": data["mana_gems"],
                "lore": data["lore"],
                "stats": data["stats"],
                "special_move": data["special_move"],
                "rarity_class": data["faction"]
            }

    # 2. Detección heurística de facción y tema si la figura es nueva o variante
    detected_faction = "Guerreros Heroicos"
    detected_theme = "castle_grayskull"
    detected_type = f"Criatura Legendaria — {sub_cat}"
    detected_emblem = "shield"
    detected_gems = ["grayskull", "gold"]

    if any(w in clean_name for w in ["skeletor", "beast", "trap", "tri-klops", "mer-man", "lyn", "faker", "scare", "clawful", "whiplash", "spikor", "stinkor", "two-bad"]):
        detected_faction = "Guerreros Diabólicos"
        detected_theme = "snake_mountain"
        detected_type = "Criatura Legendaria — Guerrero Diabólico"
        detected_emblem = "skull"
        detected_gems = ["havoc", "dark", "blood"]
    elif any(w in clean_name for w in ["hordak", "horde", "weaver", "catra", "grizzlor", "mantenna", "leech", "scorpia", "mosquitor"]):
        detected_faction = "La Horda del Terror"
        detected_theme = "evil_horde"
        detected_type = "Criatura Legendaria — Soldado de la Horda"
        detected_emblem = "bat"
        detected_gems = ["horde", "horde", "plasma"]
    elif any(w in clean_name for w in ["snake", "hiss", "khan", "rattlor", "tung", "lashr", "serpiente", "slither"]):
        detected_faction = "Los Hombres Serpiente"
        detected_theme = "snake_men"
        detected_type = "Criatura Legendaria — Hombre Serpiente"
        detected_emblem = "snake"
        detected_gems = ["snake", "snake", "poison"]
    elif any(w in clean_name for w in ["she-ra", "shera", "bow", "glimmer", "frosta", "angella", "mermista", "rebellion"]):
        detected_faction = "La Gran Rebelión"
        detected_theme = "great_rebellion"
        detected_type = "Princesa del Poder — Gran Rebelión"
        detected_emblem = "sparkles"
        detected_gems = ["rebellion", "crystal"]
    elif any(w in clean_name for w in ["zodac", "zodak", "he-ro", "eldor", "cosmic"]):
        detected_faction = "Guardianes Cósmicos"
        detected_theme = "cosmic_enforcers"
        detected_type = "Ejecutor Cósmico — Juez del Destino"
        detected_emblem = "infinity"
        detected_gems = ["cosmic", "neutral"]

    # Detección de arma y ataque
    detected_weapon = "power_sword"
    if any(w in clean_name for w in ["staff", "báculo", "baculo", "skeletor", "lyn", "orbe"]):
        detected_weapon = "havoc_staff"
    elif any(w in clean_name for w in ["axe", "hacha", "battle armor"]):
        detected_weapon = "battle_axe"
    elif any(w in clean_name for w in ["laser", "blaster", "gun", "pistol", "canon", "duncan", "tech"]):
        detected_weapon = "laser_blaster"
    elif any(w in clean_name for w in ["cat", "tiger", "gato", "beast", "panthor", "claw", "zarpazo"]):
        detected_weapon = "claws_beast"
    elif any(w in clean_name for w in ["snake", "serpiente", "venom", "khan", "rattlor", "tung"]):
        detected_weapon = "snake_venom"
    elif any(w in clean_name for w in ["thundercat", "lion-o", "mumm-ra", "augurio"]):
        detected_weapon = "sword_of_omens"
    elif any(w in clean_name for w in ["ram", "ariete", "mace", "hammer"]):
        detected_weapon = "ram_mace"
    elif any(w in clean_name for w in ["crossbow", "ballesta", "horde", "hordak"]):
        detected_weapon = "horde_crossbow"
    elif any(w in clean_name for w in ["ocean", "sea", "mer-man", "tridente", "agua"]):
        detected_weapon = "water_ocean"

    attack_pool = ATTACK_MATRIX.get(detected_weapon, ATTACK_MATRIX["power_sword"])
    hash_idx = sum(ord(c) for c in clean_name) % len(attack_pool)
    selected_attack = attack_pool[hash_idx]

    fuerza = 80 + (sum(ord(c) for c in clean_name) % 19)
    magia = 70 + ((sum(ord(c) for c in clean_name) * 3) % 29)
    defensa = 82 + ((sum(ord(c) for c in clean_name) * 7) % 17)
    agilidad = 78 + ((sum(ord(c) for c in clean_name) * 11) % 21)

    return {
        "canonical_name": product_name,
        "faction": detected_faction,
        "type_line": detected_type,
        "frame_theme": detected_theme,
        "emblem": detected_emblem,
        "mana_gems": detected_gems,
        "lore": f"Guerrero legendario de la saga {sub_cat}. Portando su armamento característico en la encarnizada batalla por el destino del cosmos, defiende el honor de su linaje en Eternia.",
        "stats": {
            "fuerza": fuerza,
            "magia": magia,
            "defensa": defensa,
            "agilidad": agilidad
        },
        "special_move": selected_attack,
        "rarity_class": detected_faction
    }

