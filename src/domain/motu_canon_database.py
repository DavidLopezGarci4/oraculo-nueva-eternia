"""
Base de Datos Canonica de Masters of the Universe para el Oraculo de Nueva Eternia.
Contiene:
- Matriz de mas de 50 ataques especiales preconfigurados asociados a armas y accesorios.
- Enciclopedia de Lore canonico y perfiles RPG para personajes de MOTU, Origins, Masterverse y Crossovers.
"""

from typing import Dict, Any, Optional, List

# 1. MATRIZ DE MAS DE 50 ATAQUES ESPECIALES MOTU POR TIPO DE ARMA / ACCESORIO
ATTACK_MATRIX: Dict[str, List[str]] = {
    "power_sword": [
        "Furia del Relampago de Grayskull",
        "Tajo Cosmico de Luz Ancestral",
        "Vortice Solar de Eternia",
        "Estocada del Poder Infinito",
        "Corte Hendidor de Titanes"
    ],
    "sword_of_omens": [
        "Furia del Ojo de Thundera",
        "Vision de Augurio Iluminador",
        "Rafaga Felina de Thundera",
        "Tajo de la Garra Escarlata",
        "Poder del Augurio Supremo"
    ],
    "havoc_staff": [
        "Descarga de Sombras Arcanas",
        "Orbe Maldito de Snake Mountain",
        "Juicio Espectral de Havoc",
        "Rayo Nigromantico del Caos",
        "Invocacion del Velo Demoniaco"
    ],
    "battle_axe": [
        "Hendidura Doble de Acero Eterniano",
        "Torbellino Devastador de Grayskull",
        "Filo Sismico de Batalla",
        "Golpe Decapitador de Titanes",
        "Quebrantahuesos de Hierro"
    ],
    "laser_blaster": [
        "Rafaga Fotonica Man-At-Arms",
        "Descarga de Iones de Plasma",
        "Disparo Termico Perforante",
        "Pulso Laser de Alta Densidad",
        "Bombardeo Optico Tactico"
    ],
    "claws_beast": [
        "Zarpazo Titanico de la Jungla",
        "Desgarro Feroz de la Selva Carmesi",
        "Embestida Bestial Salvaje",
        "Mordisco Destructor de Panthor",
        "Furia Dentada de Eternia"
    ],
    "magic_sorcery": [
        "Escudo del Halcon Mistico",
        "Lanza de Luz Arcana de Zoar",
        "Tormenta Ilusoria de Subternia",
        "Onda Psiquica de los Antiguos",
        "Canto de Proteccion de Grayskull"
    ],
    "ram_mace": [
        "Impacto de Ariete Inamovible",
        "Martillazo Sismico de Titanio",
        "Onda de Choque Terrestre",
        "Golpe Demoledor de Murallas",
        "Cabezazo de Acero Macizo"
    ],
    "horde_crossbow": [
        "Dardo Perforador de Etheria",
        "Flecha de Plasma Carmesi de la Horda",
        "Disparo de Perno Sonico",
        "Saeta Vampirica de Hordak",
        "Andanada de Espinas Asfixiantes"
    ],
    "mechanical_trap": [
        "Presa Hidraulica Trituradora",
        "Mordisco de Mandibula de Acero",
        "Garra de Extension Asesina",
        "Laser Optico de Rastreo Letal",
        "Sierra Circular de Alta Revolucion"
    ],
    "snake_venom": [
        "Azote Ofidico Venenoso",
        "Mordisco Asfixiante del Rey Hiss",
        "Chorro Acido Corrosivo",
        "Estrangulamiento de Piton Arcano",
        "Hipnosis de la Serpiente Carmesi"
    ],
    "water_ocean": [
        "Tsunami de las Profundidades de Rakash",
        "Tridente de Marea Hirviente",
        "Corriente Abisal Devastadora",
        "Invocacion del Monstruo Marino",
        "Espuma Asfixiante de los Oceanos"
    ],
    "cosmic_flight": [
        "Picado Aereo de Avion",
        "Rafaga de Viento Esmeralda",
        "Corte Alar Supersonico",
        "Descarga Cosmica de Zodac",
        "Bucle Cinetico Estratosferico"
    ]
}

ALL_SPECIAL_ATTACKS: List[str] = [atk for sublist in ATTACK_MATRIX.values() for atk in sublist]

# 2. ENCICLOPEDIA DE LORE CANONICO Y STATS RPG
MOTU_LORE_ENCYCLOPEDIA: Dict[str, Dict[str, Any]] = {
    "he-man": {
        "canonical_name": "He-Man",
        "faction": "Heroes de Grayskull",
        "lore": "Defensor supremo de los secretos de Castle Grayskull y campeon indiscutible de Eternia. Guiado por la Espada del Poder, su fuerza inquebrantable protege el universo de las garras de la oscuridad.",
        "stats": {"fuerza": 99, "magia": 88, "defensa": 95, "agilidad": 90},
        "special_move": "Furia del Relampago de Grayskull",
        "weapon_type": "power_sword"
    },
    "battle armor he-man": {
        "canonical_name": "He-Man (Battle Armor)",
        "faction": "Heroes de Grayskull",
        "lore": "Equipado con la coraza mistica forjada en las forjas sagradas para absorber los impactos mas devastadores. Cuando el combate arrecia en Eternia, este titan resiste cualquier asedio.",
        "stats": {"fuerza": 99, "magia": 86, "defensa": 99, "agilidad": 87},
        "special_move": "Hendidura Doble de Acero Eterniano",
        "weapon_type": "battle_axe"
    },
    "prince adam": {
        "canonical_name": "Principe Adam",
        "faction": "Corte Real de Eternia",
        "lore": "Heredero legitimo del trono real de Eternia y custodio secreto del mayor poder del cosmos. Bajo su aparente calma cortesana reside la voluntad del campeon del universo.",
        "stats": {"fuerza": 78, "magia": 84, "defensa": 79, "agilidad": 86},
        "special_move": "Destello de la Espada de Grayskull",
        "weapon_type": "power_sword"
    },
    "teela": {
        "canonical_name": "Teela",
        "faction": "Guardia Real de Eternia",
        "lore": "Capitana invicta de la Guardia Real y virtuosa estratega en las artes del combate cuerpo a cuerpo. Heredera del misticismo de Grayskull, lidera las tropas reales con valentia indomable.",
        "stats": {"fuerza": 85, "magia": 82, "defensa": 88, "agilidad": 94},
        "special_move": "Estocada Tactica de la Cobra",
        "weapon_type": "power_sword"
    },
    "man-at-arms": {
        "canonical_name": "Man-At-Arms (Duncan)",
        "faction": "Maestros del Universo",
        "lore": "Maestro supremo de armas e ilustre inventor de las defensas mecanicas del Palacio de Eternia. Su ingenio tecnologico y su devocion fraternal protegen a la familia real en cada crisis.",
        "stats": {"fuerza": 88, "magia": 72, "defensa": 94, "agilidad": 80},
        "special_move": "Rafaga Fotonica Man-At-Arms",
        "weapon_type": "laser_blaster"
    },
    "sorceress": {
        "canonical_name": "La Hechicera (Sorceress)",
        "faction": "Guardianes de Grayskull",
        "lore": "Guardiana mistica y alma viva de Castle Grayskull, canalizadora de la magia ancestral del cosmos. Su sabiduria milenaria guia a los campeones de la luz a traves de las eras.",
        "stats": {"fuerza": 70, "magia": 99, "defensa": 90, "agilidad": 88},
        "special_move": "Escudo del Halcon Mistico",
        "weapon_type": "magic_sorcery"
    },
    "stratos": {
        "canonical_name": "Stratos",
        "faction": "Gobernantes de Avion",
        "lore": "Monarca de la ciudad alada de Avion y soberano de las corrientes de aire de Eternia. Con sus cohetes dorsales y su vision prodigiosa domina los cielos en la lucha contra el mal.",
        "stats": {"fuerza": 84, "magia": 75, "defensa": 82, "agilidad": 98},
        "special_move": "Picado Aereo de Avion",
        "weapon_type": "cosmic_flight"
    },
    "ram man": {
        "canonical_name": "Ram Man",
        "faction": "Heroes de Grayskull",
        "lore": "Ariete humano indestructible con corazas de acero y piernas con resortes hidraulicos. Ninguna puerta de fortaleza ni formacion enemiga puede frenar su avance demoledor.",
        "stats": {"fuerza": 94, "magia": 55, "defensa": 98, "agilidad": 72},
        "special_move": "Impacto de Ariete Inamovible",
        "weapon_type": "ram_mace"
    },
    "battle cat": {
        "canonical_name": "Battle Cat (Cringer)",
        "faction": "Heroes de Grayskull",
        "lore": "Tigre de combate acorazado y fiel montura de batalla de He-Man en el fragor de la contienda. Con su rugido atronador y garras titanicas dispersa ejercitos enteros.",
        "stats": {"fuerza": 96, "magia": 74, "defensa": 92, "agilidad": 93},
        "special_move": "Desgarro Feroz de la Selva Carmesi",
        "weapon_type": "claws_beast"
    },
    "battle cat man": {
        "canonical_name": "Battle Cat Man",
        "faction": "Guerreros Hibridos de Grayskull",
        "lore": "Guerrero felino antropomorfico forjado con la ferocidad y armadura mistica de Battle Cat. Blandiendo armas de energia y su naturaleza salvaje, protege los bosques de Eternia.",
        "stats": {"fuerza": 95, "magia": 80, "defensa": 93, "agilidad": 92},
        "special_move": "Zarpazo Titanico de la Jungla",
        "weapon_type": "claws_beast"
    },
    "moss man": {
        "canonical_name": "Moss Man",
        "faction": "Espiritus de la Naturaleza",
        "lore": "Senor ancestral de la flora eterniana capaz de fusionarse con la vegetacion y controlar las raices vivientes. Guardian pacifico que despierta una furia imparable ante la tirania.",
        "stats": {"fuerza": 88, "magia": 92, "defensa": 90, "agilidad": 84},
        "special_move": "Enredo de Raices Primordiales",
        "weapon_type": "magic_sorcery"
    },
    "zodac": {
        "canonical_name": "Zodac",
        "faction": "Ejecutores Cosmicos",
        "lore": "Enforcer Cosmico neutral que vela por el equilibrio universal entre la luz y las sombras. Con su silla flotante y conocimiento infinito interviene solo cuando el destino pende de un hilo.",
        "stats": {"fuerza": 90, "magia": 95, "defensa": 92, "agilidad": 91},
        "special_move": "Descarga Cosmica de Zodac",
        "weapon_type": "cosmic_flight"
    },
    "roboto": {
        "canonical_name": "Roboto",
        "faction": "Heroes de Grayskull",
        "lore": "Guerrero mecanico consciente dotado de un corazon de compasion y engranajes de precision infinita. Sus aditamentos intercambiables lo convierten en un arsenal andante.",
        "stats": {"fuerza": 91, "magia": 60, "defensa": 96, "agilidad": 78},
        "special_move": "Presa Hidraulica Trituradora",
        "weapon_type": "mechanical_trap"
    },
    "skeletor": {
        "canonical_name": "Skeletor",
        "faction": "Guerreros Diabolicos de Snake Mountain",
        "lore": "Senor de la destruccion y tirano nigromantico de Snake Mountain cuya sed de conquista amenaza la existencia. Empunando el Baculo del Caos, canaliza las artes oscuras prohibidas de Subternia.",
        "stats": {"fuerza": 92, "magia": 99, "defensa": 88, "agilidad": 89},
        "special_move": "Descarga de Sombras Arcanas",
        "weapon_type": "havoc_staff"
    },
    "battle armor skeletor": {
        "canonical_name": "Skeletor (Battle Armor)",
        "faction": "Guerreros Diabolicos de Snake Mountain",
        "lore": "Protegido por una armadura oscura blindada forjada en las cavernas sulfurosas del inframundo. Listo para liderar la invasion definitiva sobre las almenas de Grayskull.",
        "stats": {"fuerza": 94, "magia": 98, "defensa": 97, "agilidad": 86},
        "special_move": "Juicio Espectral de Havoc",
        "weapon_type": "havoc_staff"
    },
    "evil-lyn": {
        "canonical_name": "Evil-Lyn",
        "faction": "Guerreros Diabolicos de Snake Mountain",
        "lore": "Hechicera de las sombras y maquiavelica consejera en la corte de Skeletor. Con su orbe de adivinacion y conjuros arcanos dobla la realidad a su siniestra voluntad.",
        "stats": {"fuerza": 75, "magia": 97, "defensa": 80, "agilidad": 90},
        "special_move": "Tormenta Ilusoria de Subternia",
        "weapon_type": "magic_sorcery"
    },
    "trap jaw": {
        "canonical_name": "Trap Jaw",
        "faction": "Guerreros Diabolicos de Snake Mountain",
        "lore": "Ciborg mercenario letal con mandibula de hierro capaz de triturar cualquier aleacion del cosmos. Su brazo biomecanico intercambiable porta herramientas de aniquilacion pura.",
        "stats": {"fuerza": 93, "magia": 62, "defensa": 95, "agilidad": 82},
        "special_move": "Mordisco de Mandibula de Acero",
        "weapon_type": "mechanical_trap"
    },
    "tri-klops": {
        "canonical_name": "Tri-Klops",
        "faction": "Guerreros Diabolicos de Snake Mountain",
        "lore": "Espadachin y rastreador supremo cuyo visor rotatorio le confiere vision nocturna, termica y rayos gama destructivos. Un combatiente metodico y despiadado.",
        "stats": {"fuerza": 89, "magia": 70, "defensa": 87, "agilidad": 93},
        "special_move": "Laser Optico de Rastreo Letal",
        "weapon_type": "mechanical_trap"
    },
    "beast man": {
        "canonical_name": "Beast Man",
        "faction": "Guerreros Diabolicos de Snake Mountain",
        "lore": "Senor salvaje de las bestias de Eternia y leal esbirro de Skeletor. Con su latigo ardiente y telepatia animal doblega a las criaturas mas letales.",
        "stats": {"fuerza": 92, "magia": 68, "defensa": 89, "agilidad": 86},
        "special_move": "Embestida Bestial Salvaje",
        "weapon_type": "claws_beast"
    },
    "mer-man": {
        "canonical_name": "Mer-Man",
        "faction": "Senores de los Oceanos de Rakash",
        "lore": "Soberano indiscutible del reino acuatico de Rakash y amo de los leviatanes submarinos. Con su tridente y control de las mareas arrastra a sus enemigos al abismo.",
        "stats": {"fuerza": 87, "magia": 85, "defensa": 86, "agilidad": 92},
        "special_move": "Tsunami de las Profundidades de Rakash",
        "weapon_type": "water_ocean"
    },
    "faker": {
        "canonical_name": "Faker",
        "faction": "Creaciones de Snake Mountain",
        "lore": "Duplicado cibernetico perverso de He-Man con piel azulada y circuitos frios bajo el pecho. Creado para sembrar la confusion y destruir la esperanza en Eternia.",
        "stats": {"fuerza": 97, "magia": 76, "defensa": 94, "agilidad": 88},
        "special_move": "Tajo Cosmico de Luz Ancestral",
        "weapon_type": "power_sword"
    },
    "scare glow": {
        "canonical_name": "Scare Glow",
        "faction": "Espiritus del Inframundo",
        "lore": "Fantasma esqueletico refulgente que infunde un pavor paralizante en los corazones mas valientes. Portando su guadana de la muerte acecha en las noches de Eternia.",
        "stats": {"fuerza": 86, "magia": 96, "defensa": 84, "agilidad": 89},
        "special_move": "Juicio Espectral de Havoc",
        "weapon_type": "havoc_staff"
    },
    "clawful": {
        "canonical_name": "Clawful",
        "faction": "Guerreros Diabolicos de Snake Mountain",
        "lore": "Bruto acorazado con una pinza descomunal capaz de pulverizar rocas y escudos de Grayskull. Su caparazon impenetrable lo vuelve una pesadilla en combate frontal.",
        "stats": {"fuerza": 94, "magia": 50, "defensa": 97, "agilidad": 74},
        "special_move": "Presa Hidraulica Trituradora",
        "weapon_type": "mechanical_trap"
    },
    "whiplash": {
        "canonical_name": "Whiplash",
        "faction": "Guerreros Diabolicos de Snake Mountain",
        "lore": "Reptil de combate dotado de una cola masiva que azota con la potencia de un ariete. Su agilidad anfibia y piel escamosa lo convierten en un demoledor implacable.",
        "stats": {"fuerza": 91, "magia": 56, "defensa": 92, "agilidad": 88},
        "special_move": "Azote Ofidico Venenoso",
        "weapon_type": "snake_venom"
    },
    "hordak": {
        "canonical_name": "Hordak",
        "faction": "Imperio de la Horda del Terror",
        "lore": "Tirano supremo de la Zona del Terror y maestro de la tecno-magia oscura. Capaz de transmutar su propio cuerpo en armamento mecanico para subyugar mundos enteros.",
        "stats": {"fuerza": 95, "magia": 96, "defensa": 95, "agilidad": 87},
        "special_move": "Flecha de Plasma Carmesi de la Horda",
        "weapon_type": "horde_crossbow"
    },
    "king hiss": {
        "canonical_name": "Rey Hiss (King Hiss)",
        "faction": "Imperio de los Hombres Serpiente",
        "lore": "Antiquisimo monarca ofidico cuyo disfraz humano oculta una masa de serpientes devoradoras. Regresa de las sombras del pasado para reclamar el dominio de Eternia.",
        "stats": {"fuerza": 93, "magia": 95, "defensa": 91, "agilidad": 93},
        "special_move": "Mordisco Asfixiante del Rey Hiss",
        "weapon_type": "snake_venom"
    },
    "kobra khan": {
        "canonical_name": "Kobra Khan",
        "faction": "Imperio de los Hombres Serpiente",
        "lore": "Guerillero reptiliano capaz de expulsar una niebla soporifera y acido mortal desde su garganta. Un emboscador maestro de las marismas eternianas.",
        "stats": {"fuerza": 84, "magia": 78, "defensa": 85, "agilidad": 91},
        "special_move": "Chorro Acido Corrosivo",
        "weapon_type": "snake_venom"
    },
    "lion-o": {
        "canonical_name": "Lion-O",
        "faction": "Alianza Thundercats & Eternia",
        "lore": "Senor noble de los Thundercats y portador de la legendaria Espada del Augurio. En su alianza mistica con los campeones de Grayskull, canaliza el Ojo de Thundera contra la oscuridad cosmica.",
        "stats": {"fuerza": 96, "magia": 92, "defensa": 93, "agilidad": 97},
        "special_move": "Furia del Ojo de Thundera",
        "weapon_type": "sword_of_omens"
    },
    "mumm-ra": {
        "canonical_name": "Mumm-Ra el Inmortal",
        "faction": "Fuerzas Oscuras del Cosmos",
        "lore": "Sacerdote milenario y conducto de los Antiguos Espiritus del Mal. Al transformarse en su forma imperecedera, desata una catastrofe de poder destructivo.",
        "stats": {"fuerza": 96, "magia": 99, "defensa": 94, "agilidad": 86},
        "special_move": "Descarga de Sombras Arcanas",
        "weapon_type": "havoc_staff"
    }
}

def resolve_motu_profile(product_name: str, sub_category: Optional[str] = "MOTU Origins") -> Dict[str, Any]:
    clean_name = product_name.lower().strip()
    sub_cat = sub_category or "MOTU Origins"

    for key, data in MOTU_LORE_ENCYCLOPEDIA.items():
        if key in clean_name:
            return {
                "lore": data["lore"],
                "stats": data["stats"],
                "special_move": data["special_move"],
                "rarity_class": data["faction"]
            }

    detected_weapon = "power_sword"
    if any(w in clean_name for w in ["staff", "baculo", "skeletor", "lyn", "orbe"]):
        detected_weapon = "havoc_staff"
    elif any(w in clean_name for w in ["axe", "hacha", "battle armor"]):
        detected_weapon = "battle_axe"
    elif any(w in clean_name for w in ["laser", "blaster", "gun", "pistol", "canon", "duncan", "tech"]):
        detected_weapon = "laser_blaster"
    elif any(w in clean_name for w in ["cat", "tiger", "gato", "beast", "panthor", "claw", "zarpazo"]):
        detected_weapon = "claws_beast"
    elif any(w in clean_name for w in ["snake", "serpiente", "venom", "khan", "rattlor", "tung"]):
        detected_weapon = "snake_venom"
    elif any(w in clean_name for w in ["thundercat", "lion-o", "mumm-ra", "cheetara", "panthro", "augurio"]):
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

    fuerza = 78 + (sum(ord(c) for c in clean_name) % 21)
    magia = 72 + ((sum(ord(c) for c in clean_name) * 3) % 27)
    defensa = 80 + ((sum(ord(c) for c in clean_name) * 7) % 19)
    agilidad = 75 + ((sum(ord(c) for c in clean_name) * 11) % 24)

    return {
        "lore": f"Guerrero legendario de la saga {sub_cat}. Portando su armamento caracteristico en la encarnizada batalla por el destino de Grayskull, desata todo su potencial en el campo de batalla de Eternia.",
        "stats": {
            "fuerza": fuerza,
            "magia": magia,
            "defensa": defensa,
            "agilidad": agilidad
        },
        "special_move": selected_attack,
        "rarity_class": f"Guardian de {sub_cat}"
    }
