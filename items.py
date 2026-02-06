"""
Système complet d'objets, d'équipement et de loot.
Tags : type + matériau + élément optionnel.
Génération procédurale adaptée au floor_level.
"""

import random
import math

# ==========================================
# MATÉRIAUX (ordre croissant de puissance)
# ==========================================

MATERIALS = {
    "Bois":    {"tier": 1, "multiplier": 0.6,  "color": (139, 90, 43),    "floors": (1, 15)},
    "Pierre":  {"tier": 2, "multiplier": 0.8,  "color": (140, 140, 140),  "floors": (1, 25)},
    "Fer":     {"tier": 3, "multiplier": 1.0,  "color": (200, 200, 200),  "floors": (3, 40)},
    "Argent":  {"tier": 4, "multiplier": 1.3,  "color": (220, 220, 255),  "floors": (10, 60)},
    "Or":      {"tier": 5, "multiplier": 1.6,  "color": (255, 215, 0),    "floors": (20, 80)},
    "Mythril": {"tier": 6, "multiplier": 2.0,  "color": (150, 200, 255),  "floors": (35, 100)},
}

# ==========================================
# ÉLÉMENTS (optionnels, ~30% de chance)
# ==========================================

ELEMENTS = {
    "Feu":      {"bonus_attack": 3, "bonus_defense": 0, "color": (255, 80, 30)},
    "Glace":    {"bonus_attack": 2, "bonus_defense": 1, "color": (100, 200, 255)},
    "Foudre":   {"bonus_attack": 4, "bonus_defense": 0, "color": (255, 255, 100)},
    "Poison":   {"bonus_attack": 2, "bonus_defense": 0, "color": (100, 255, 50)},
    "Sacré":    {"bonus_attack": 1, "bonus_defense": 3, "color": (255, 255, 220)},
    "Ténèbres": {"bonus_attack": 3, "bonus_defense": 1, "color": (150, 50, 200)},
}

# ==========================================
# TYPES D'ARMES
# ==========================================

WEAPON_TYPES = {
    # Mêlée
    "Épée":   {"base_attack": 10, "slot": "main_hand", "two_handed": False, "symbol": "/",  "category": "melee"},
    "Hache":  {"base_attack": 13, "slot": "main_hand", "two_handed": False, "symbol": "P",  "category": "melee"},
    "Dague":  {"base_attack": 6,  "slot": "main_hand", "two_handed": False, "symbol": "-",  "category": "melee"},
    "Masse":  {"base_attack": 11, "slot": "main_hand", "two_handed": False, "symbol": "T",  "category": "melee"},
    "Lance":  {"base_attack": 12, "slot": "main_hand", "two_handed": True,  "symbol": "|",  "category": "melee"},
    # Distance
    "Arc":    {"base_attack": 9,  "slot": "main_hand", "two_handed": True,  "symbol": ")",  "category": "ranged"},
    # Magiques
    "Bâton":    {"base_attack": 7,  "slot": "main_hand", "two_handed": True,  "symbol": "\\", "category": "magic"},
    "Baguette": {"base_attack": 5,  "slot": "main_hand", "two_handed": False, "symbol": "~",  "category": "magic"},
    "Orbe":     {"base_attack": 8,  "slot": "main_hand", "two_handed": False, "symbol": "o",  "category": "magic"},
    "Grimoire": {"base_attack": 9,  "slot": "main_hand", "two_handed": False, "symbol": "\"", "category": "magic"},
}

# ==========================================
# TYPES D'ARMURES
# ==========================================

ARMOR_TYPES = {
    "Armure":  {"base_defense": 8,  "slot": "body",  "symbol": "[", "category": "heavy"},
    "Casque":  {"base_defense": 4,  "slot": "head",  "symbol": "^", "category": "heavy"},
    "Gants":   {"base_defense": 3,  "slot": "hands", "symbol": "{", "category": "heavy"},
    "Bottes":  {"base_defense": 3,  "slot": "feet",  "symbol": "}", "category": "heavy"},
}

# ==========================================
# BOUCLIER
# ==========================================

SHIELD_TYPE = {
    "Bouclier": {"base_defense": 6, "slot": "off_hand", "symbol": "]", "category": "shield"},
}

# ==========================================
# ACCESSOIRES
# ==========================================

ACCESSORY_TYPES = {
    "Anneau":  {"slot_options": ["ring1", "ring2"], "symbol": "=", "category": "accessory"},
    "Amulette": {"slot_options": ["amulet"],        "symbol": "\"", "category": "accessory"},
}

ACCESSORY_BONUSES = {
    "Force":     {"attack": 3},
    "Protection": {"defense": 3},
    "Vitalité":  {"max_hp": 15},
    "Arcane":    {"max_mana": 10},
    "Endurance": {"max_hunger": 20},
}

# ==========================================
# NOURRITURE
# ==========================================

FOOD_TYPES = {
    "Ration":  {"hunger_restore": 30, "symbol": "%", "color": (255, 200, 100)},
    "Pain":    {"hunger_restore": 20, "symbol": "%", "color": (210, 180, 140)},
    "Viande":  {"hunger_restore": 50, "symbol": "%", "color": (200, 100, 100)},
}

# ==========================================
# GÉNÉRATION D'OBJETS
# ==========================================

def _pick_material(floor_level):
    """Choisit un matériau adapté à l'étage avec pondération"""
    available = []
    weights = []
    for name, data in MATERIALS.items():
        min_floor, max_floor = data["floors"]
        if floor_level >= min_floor:
            # Poids gaussien centré sur le milieu de la plage
            center = (min_floor + max_floor) / 2
            sigma = (max_floor - min_floor) / 3
            weight = math.exp(-0.5 * ((floor_level - center) / max(sigma, 1)) ** 2)
            available.append(name)
            weights.append(max(weight, 0.05))
    if not available:
        return "Bois"
    return random.choices(available, weights=weights, k=1)[0]


def _pick_element():
    """30% de chance d'avoir un élément, sinon None"""
    if random.random() < 0.3:
        return random.choice(list(ELEMENTS.keys()))
    return None


def _build_name(item_type_name, material_name, element_name):
    """Construit le nom de l'objet : 'Épée en Fer de Feu'"""
    name = f"{item_type_name} en {material_name}"
    if element_name:
        # Adapter la préposition selon l'élément
        if element_name in ("Feu", "Glace", "Poison"):
            name += f" de {element_name}"
        elif element_name == "Foudre":
            name += " de Foudre"
        elif element_name == "Sacré":
            name += " Sacré" if item_type_name in ("Bouclier", "Grimoire", "Orbe", "Arc", "Bâton") else " Sacrée"
        elif element_name == "Ténèbres":
            name += " des Ténèbres"
    return name


def generate_weapon(floor_level):
    """Génère une arme aléatoire adaptée à l'étage"""
    weapon_name = random.choice(list(WEAPON_TYPES.keys()))
    weapon_data = WEAPON_TYPES[weapon_name]
    material = _pick_material(floor_level)
    mat_data = MATERIALS[material]
    element = _pick_element()

    attack = int(weapon_data["base_attack"] * mat_data["multiplier"])
    elemental_attack = 0
    tags = [weapon_name, material]

    if element:
        tags.append(element)
        elemental_attack = ELEMENTS[element]["bonus_attack"]

    return {
        "name": _build_name(weapon_name, material, element),
        "type": "weapon",
        "weapon_type": weapon_name,
        "slot": weapon_data["slot"],
        "two_handed": weapon_data["two_handed"],
        "tags": tags,
        "attack": attack,
        "elemental_attack": elemental_attack,
        "element": element,
        "defense": 0,
        "bonuses": {},
        "level": 1,
        "symbol": weapon_data["symbol"],
        "color": ELEMENTS[element]["color"] if element else mat_data["color"],
        "equipped": False,
        "equipped_slot": None,
    }


def generate_armor(floor_level):
    """Génère une armure aléatoire adaptée à l'étage"""
    armor_name = random.choice(list(ARMOR_TYPES.keys()))
    armor_data = ARMOR_TYPES[armor_name]
    material = _pick_material(floor_level)
    mat_data = MATERIALS[material]
    element = _pick_element()

    defense = int(armor_data["base_defense"] * mat_data["multiplier"])
    elemental_defense = 0
    tags = [armor_name, material]

    if element:
        tags.append(element)
        elemental_defense = ELEMENTS[element]["bonus_defense"]

    return {
        "name": _build_name(armor_name, material, element),
        "type": "armor",
        "armor_type": armor_name,
        "slot": armor_data["slot"],
        "two_handed": False,
        "tags": tags,
        "attack": 0,
        "elemental_attack": 0,
        "element": element,
        "defense": defense + elemental_defense,
        "bonuses": {},
        "level": 1,
        "symbol": armor_data["symbol"],
        "color": ELEMENTS[element]["color"] if element else mat_data["color"],
        "equipped": False,
        "equipped_slot": None,
    }


def generate_shield(floor_level):
    """Génère un bouclier aléatoire"""
    shield_data = SHIELD_TYPE["Bouclier"]
    material = _pick_material(floor_level)
    mat_data = MATERIALS[material]
    element = _pick_element()

    defense = int(shield_data["base_defense"] * mat_data["multiplier"])
    elemental_defense = 0
    tags = ["Bouclier", material]

    if element:
        tags.append(element)
        elemental_defense = ELEMENTS[element]["bonus_defense"]

    return {
        "name": _build_name("Bouclier", material, element),
        "type": "shield",
        "slot": "off_hand",
        "two_handed": False,
        "tags": tags,
        "attack": 0,
        "elemental_attack": 0,
        "element": element,
        "defense": defense + elemental_defense,
        "bonuses": {},
        "level": 1,
        "symbol": shield_data["symbol"],
        "color": ELEMENTS[element]["color"] if element else mat_data["color"],
        "equipped": False,
        "equipped_slot": None,
    }


def generate_accessory(floor_level):
    """Génère un accessoire aléatoire (anneau ou amulette)"""
    acc_name = random.choice(list(ACCESSORY_TYPES.keys()))
    acc_data = ACCESSORY_TYPES[acc_name]
    bonus_name = random.choice(list(ACCESSORY_BONUSES.keys()))
    bonus_data = ACCESSORY_BONUSES[bonus_name]
    material = _pick_material(floor_level)
    mat_data = MATERIALS[material]

    # Scaling des bonus avec le matériau
    scaled_bonuses = {}
    for stat, value in bonus_data.items():
        scaled_bonuses[stat] = int(value * mat_data["multiplier"])

    tags = [acc_name, material]
    name = f"{acc_name} de {bonus_name} en {material}"

    return {
        "name": name,
        "type": "accessory",
        "accessory_type": acc_name,
        "slot": acc_data["slot_options"][0],
        "slot_options": acc_data["slot_options"],
        "two_handed": False,
        "tags": tags,
        "attack": 0,
        "elemental_attack": 0,
        "element": None,
        "defense": 0,
        "bonuses": scaled_bonuses,
        "level": 1,
        "symbol": acc_data["symbol"],
        "color": mat_data["color"],
        "equipped": False,
        "equipped_slot": None,
    }


def generate_food():
    """Génère de la nourriture aléatoire"""
    food_name = random.choice(list(FOOD_TYPES.keys()))
    food_data = FOOD_TYPES[food_name]

    return {
        "name": food_name,
        "type": "food",
        "slot": None,
        "two_handed": False,
        "tags": [food_name],
        "attack": 0,
        "defense": 0,
        "bonuses": {},
        "hunger_restore": food_data["hunger_restore"],
        "level": 0,
        "symbol": food_data["symbol"],
        "color": food_data["color"],
        "equipped": False,
        "equipped_slot": None,
    }


def generate_item(floor_level):
    """Génère un objet aléatoire adapté à l'étage"""
    # Probabilités : 30% arme, 25% armure, 10% bouclier, 10% accessoire, 25% nourriture
    roll = random.random()
    if roll < 0.30:
        return generate_weapon(floor_level)
    elif roll < 0.55:
        return generate_armor(floor_level)
    elif roll < 0.65:
        return generate_shield(floor_level)
    elif roll < 0.75:
        return generate_accessory(floor_level)
    else:
        return generate_food()


def spawn_items(num_items, rooms, game_map, MAP_WIDTH, MAP_HEIGHT, floor_level=1):
    """Crée des objets aléatoires sur la carte, adaptés à l'étage"""
    items = []
    # 3-8 objets par étage
    count = random.randint(max(3, num_items), max(num_items, 8))

    for _ in range(count):
        attempts = 0
        while attempts < 100:
            x = random.randint(2, MAP_WIDTH - 3)
            y = random.randint(2, MAP_HEIGHT - 3)

            if game_map[y][x] == '.':
                if not any(item["x"] == x and item["y"] == y for item in items):
                    item = generate_item(floor_level)
                    item["x"] = x
                    item["y"] = y
                    items.append(item)
                    break
            attempts += 1

    return items
