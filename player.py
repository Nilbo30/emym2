"""
Gestion du joueur, de sa vision et de ses slots d'équipement
"""

# Slots d'équipement disponibles
EQUIPMENT_SLOTS = ["main_hand", "off_hand", "body", "head", "hands", "feet", "ring1", "ring2", "amulet"]

# Dictionnaire du joueur (toutes ses stats)
player = {
    "x": 5,
    "y": 5,
    # Stats de base (sans équipement)
    "base_attack": 10,
    "base_defense": 5,
    "hp": 100,
    "max_hp": 100,
    "mana": 50,
    "max_mana": 50,
    "attack": 10,
    "defense": 5,
    "hunger": 100,
    "max_hunger": 100,
    "step_counter": 0,
    # Slots d'équipement : chaque slot contient l'item ou None
    "equipment": {
        "main_hand": None,
        "off_hand": None,
        "body": None,
        "head": None,
        "hands": None,
        "feet": None,
        "ring1": None,
        "ring2": None,
        "amulet": None,
    },
}

# Nombre de pas avant de perdre 1 point de faim
STEPS_PER_HUNGER = 3


def calculate_visible_tiles(player_x, player_y, vision_radius):
    """
    Calcule quelles cases sont visibles autour du joueur
    Retourne une liste de tuples (x, y)
    """
    visible = []

    for y in range(player_y - vision_radius, player_y + vision_radius + 1):
        for x in range(player_x - vision_radius, player_x + vision_radius + 1):
            distance = ((x - player_x)**2 + (y - player_y)**2) ** 0.5
            if distance <= vision_radius:
                visible.append((x, y))

    return visible


def recalculate_stats():
    """Recalcule attack/defense/bonuses du joueur d'après l'équipement"""
    total_attack = player["base_attack"]
    total_defense = player["base_defense"]
    bonus_max_hp = 0
    bonus_max_mana = 0
    bonus_max_hunger = 0

    for slot_name, item in player["equipment"].items():
        if item is None:
            continue
        total_attack += item.get("attack", 0) + item.get("elemental_attack", 0)
        total_defense += item.get("defense", 0)
        # Bonuses d'accessoires
        for stat, value in item.get("bonuses", {}).items():
            if stat == "attack":
                total_attack += value
            elif stat == "defense":
                total_defense += value
            elif stat == "max_hp":
                bonus_max_hp += value
            elif stat == "max_mana":
                bonus_max_mana += value
            elif stat == "max_hunger":
                bonus_max_hunger += value

    player["attack"] = total_attack
    player["defense"] = total_defense
    player["max_hp"] = 100 + bonus_max_hp
    player["max_mana"] = 50 + bonus_max_mana
    player["max_hunger"] = 100 + bonus_max_hunger

    # Clamper les valeurs courantes
    if player["hp"] > player["max_hp"]:
        player["hp"] = player["max_hp"]
    if player["mana"] > player["max_mana"]:
        player["mana"] = player["max_mana"]
    if player["hunger"] > player["max_hunger"]:
        player["hunger"] = player["max_hunger"]


def equip_to_slot(item, slot):
    """
    Équipe un item dans un slot spécifique.
    Retourne l'item précédemment dans le slot (ou None).
    Gère les armes à deux mains.
    """
    old_item = player["equipment"][slot]

    # Déséquiper l'ancien item du slot
    if old_item is not None:
        old_item["equipped"] = False
        old_item["equipped_slot"] = None

    # Si c'est une arme à deux mains, libérer aussi off_hand
    if item.get("two_handed"):
        off_item = player["equipment"].get("off_hand")
        if off_item is not None and off_item != old_item:
            off_item["equipped"] = False
            off_item["equipped_slot"] = None
            player["equipment"]["off_hand"] = None

    # Si on équipe en off_hand, vérifier que main_hand n'est pas deux mains
    if slot == "off_hand":
        main_item = player["equipment"].get("main_hand")
        if main_item is not None and main_item.get("two_handed"):
            main_item["equipped"] = False
            main_item["equipped_slot"] = None
            player["equipment"]["main_hand"] = None

    # Équiper le nouvel item
    player["equipment"][slot] = item
    item["equipped"] = True
    item["equipped_slot"] = slot

    # Recalculer les stats
    recalculate_stats()
    return old_item


def unequip_slot(slot):
    """Déséquipe le slot donné. Retourne l'item retiré ou None."""
    item = player["equipment"].get(slot)
    if item is None:
        return None

    item["equipped"] = False
    item["equipped_slot"] = None
    player["equipment"][slot] = None

    recalculate_stats()
    return item


def get_valid_slot_for_item(item):
    """
    Détermine le meilleur slot pour un item.
    Retourne le nom du slot ou None si pas équipable.
    """
    item_type = item.get("type")

    if item_type == "weapon":
        return "main_hand"

    elif item_type == "shield":
        return "off_hand"

    elif item_type == "armor":
        return item.get("slot", "body")

    elif item_type == "accessory":
        slot_options = item.get("slot_options", [])
        if not slot_options:
            return None
        # Pour les anneaux, choisir le premier slot libre
        for s in slot_options:
            if player["equipment"].get(s) is None:
                return s
        # Sinon le premier slot
        return slot_options[0]

    return None


def reset_player(first_room):
    """Réinitialise le joueur (au début ou après game over)"""
    player["hp"] = 100
    player["max_hp"] = 100
    player["mana"] = 50
    player["max_mana"] = 50
    player["base_attack"] = 10
    player["base_defense"] = 5
    player["attack"] = 10
    player["defense"] = 5
    player["hunger"] = 100
    player["max_hunger"] = 100
    player["step_counter"] = 0

    # Vider tous les slots
    for slot in EQUIPMENT_SLOTS:
        player["equipment"][slot] = None

    # Position dans la première salle
    if first_room:
        player["x"] = first_room["x"] + 1
        player["y"] = first_room["y"] + 1
    else:
        player["x"] = 5
        player["y"] = 5


def spawn_player_in_room(first_room):
    """Place le joueur dans une salle (début d'étage)"""
    if first_room:
        player["x"] = first_room["x"] + 1
        player["y"] = first_room["y"] + 1
    else:
        player["x"] = 5
        player["y"] = 5


def check_hunger():
    """Gère les effets de la faim - Retourne True si le joueur meurt"""
    if player["hunger"] <= 0:
        player["hunger"] = 0
        player["hp"] -= 1
        print("Vous mourez de faim ! -1 HP")
        return player["hp"] <= 0
    elif player["hunger"] > player["max_hunger"]:
        player["hunger"] = player["max_hunger"]
    return False
