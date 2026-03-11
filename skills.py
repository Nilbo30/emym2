"""
Système de compétences skill-by-use.
Chaque type d'équipement a sa propre compétence qui monte avec l'utilisation.
"""

import math

# ==========================================
# MAPPING ARMES → SKILLS
# ==========================================

WEAPON_SKILL_MAP = {
    "Épée": "sword",
    "Hache": "axe",
    "Dague": "dagger",
    "Masse": "mace",
    "Lance": "spear",
    "Arc": "bow",
    "Arbalète": "crossbow",
    "Bâton": "staff",
    "Baguette": "wand",
    "Orbe": "orb",
    "Grimoire": "grimoire",
}

# MAPPING SLOTS ARMURE → SKILLS
SLOT_SKILL_MAP = {
    "head": "head_armor",
    "body": "torso_armor",
    "legs": "legs_armor",
    "hands": "hands_armor",
    "feet": "feet_armor",
    "off_hand": "shield",
    "amulet": "amulet",
    "ring1": "ring",
    "ring2": "ring",
}

# ==========================================
# DÉFINITION DE TOUS LES SKILLS
# ==========================================

def _create_skill(name, key, category, bonus_type, bonus_per_level=0.5):
    return {
        "name": name,
        "key": key,
        "level": 0,
        "xp": 0.0,
        "category": category,
        "bonus_type": bonus_type,
        "bonus_per_level": bonus_per_level,
    }

def _init_skills():
    """Crée le dictionnaire initial de tous les skills"""
    return {
        # Armes
        "sword":    _create_skill("Épée", "sword", "weapon", "attack"),
        "axe":      _create_skill("Hache", "axe", "weapon", "attack"),
        "dagger":   _create_skill("Dague", "dagger", "weapon", "attack"),
        "mace":     _create_skill("Masse", "mace", "weapon", "attack"),
        "spear":    _create_skill("Lance", "spear", "weapon", "attack"),
        "bow":      _create_skill("Arc", "bow", "weapon", "attack"),
        "crossbow": _create_skill("Arbalète", "crossbow", "weapon", "attack"),
        "staff":    _create_skill("Bâton", "staff", "weapon", "attack"),
        "wand":     _create_skill("Baguette", "wand", "weapon", "attack"),
        "orb":      _create_skill("Orbe", "orb", "weapon", "attack"),
        "grimoire": _create_skill("Grimoire", "grimoire", "weapon", "attack"),
        # Armures
        "head_armor":  _create_skill("Casque", "head_armor", "armor", "defense"),
        "torso_armor": _create_skill("Plastron", "torso_armor", "armor", "defense"),
        "legs_armor":  _create_skill("Jambières", "legs_armor", "armor", "defense"),
        "hands_armor": _create_skill("Gants", "hands_armor", "armor", "defense"),
        "feet_armor":  _create_skill("Bottes", "feet_armor", "armor", "defense"),
        "shield":      _create_skill("Bouclier", "shield", "armor", "defense"),
        # Accessoires
        "amulet": _create_skill("Amulette", "amulet", "accessory", "efficacy", 0.3),
        "ring":   _create_skill("Anneau", "ring", "accessory", "efficacy", 0.3),
    }

# Dictionnaire global des skills
skills = _init_skills()


# ==========================================
# FORMULE DE PROGRESSION
# ==========================================

def xp_for_next_level(current_level):
    """XP nécessaire pour passer au niveau suivant (courbe log, pas de cap)"""
    base = 10
    return base * math.log(current_level + 2) * (1 + current_level * 0.1)


# ==========================================
# FONCTIONS PUBLIQUES
# ==========================================

def gain_xp(skill_key, amount=1.0):
    """Ajoute de l'XP à un skill. Gère le level up automatiquement."""
    if skill_key not in skills:
        return

    skill = skills[skill_key]
    skill["xp"] += amount

    # Vérifier level up (possiblement plusieurs d'un coup)
    while skill["xp"] >= xp_for_next_level(skill["level"]):
        skill["xp"] -= xp_for_next_level(skill["level"])
        skill["level"] += 1
        bonus = skill["level"] * skill["bonus_per_level"]
        bonus_label = "ATK" if skill["bonus_type"] == "attack" else "DEF" if skill["bonus_type"] == "defense" else "efficacite"
        print(f"[SKILL UP] {skill['name']} : niveau {skill['level']} ! (+{bonus:.1f} {bonus_label})")

        # Recalculer les stats du joueur après level up
        from player import recalculate_stats
        recalculate_stats()


def get_skill_level(skill_key):
    """Retourne le niveau actuel d'un skill"""
    if skill_key not in skills:
        return 0
    return skills[skill_key]["level"]


def get_skill_bonus(skill_key):
    """Retourne le bonus total du skill (level * bonus_per_level)"""
    if skill_key not in skills:
        return 0.0
    skill = skills[skill_key]
    return skill["level"] * skill["bonus_per_level"]


def get_all_skills():
    """Retourne tous les skills (pour l'écran de stats)"""
    return skills


def get_xp_progress(skill_key):
    """Retourne (xp_actuelle, xp_nécessaire) pour le prochain niveau"""
    if skill_key not in skills:
        return 0.0, 1.0
    skill = skills[skill_key]
    return skill["xp"], xp_for_next_level(skill["level"])


def reset_skills():
    """Remet tous les skills à 0 (pour game over)"""
    global skills
    skills = _init_skills()


def get_weapon_skill_key(weapon_type_name):
    """Convertit un weapon_type (ex: 'Épée') en skill_key (ex: 'sword')"""
    return WEAPON_SKILL_MAP.get(weapon_type_name)


def tick_armor_xp():
    """
    Appelée chaque tour : donne 0.1 XP passive aux skills d'armure/accessoire portés.
    """
    from player import player

    for slot_name, item in player["equipment"].items():
        if item is None:
            continue
        # Déterminer le skill correspondant au slot
        skill_key = _get_skill_for_slot(slot_name, item)
        if skill_key:
            gain_xp(skill_key, 0.1)


def on_hit_armor_xp():
    """
    Appelée quand le joueur se fait toucher en combat :
    donne 0.3 XP bonus aux skills d'armure/accessoire portés.
    """
    from player import player

    for slot_name, item in player["equipment"].items():
        if item is None:
            continue
        skill_key = _get_skill_for_slot(slot_name, item)
        if skill_key:
            gain_xp(skill_key, 0.3)


def _get_skill_for_slot(slot_name, item):
    """Détermine le skill_key pour un item dans un slot donné"""
    # Slot main_hand → pas un skill d'armure (c'est une arme)
    if slot_name == "main_hand":
        return None

    # off_hand → skill "shield" seulement si c'est un bouclier
    if slot_name == "off_hand":
        if item.get("type") == "shield":
            return "shield"
        return None

    return SLOT_SKILL_MAP.get(slot_name)
