"""
Système de races et classes pour les ennemis
25 races fantasy + 10 classes génériques
Courbes de probabilité d'apparition par étage (1-100)
"""

import math
import random


# ==========================================
# 25 RACES FANTASY
# ==========================================
#
# Chaque race définit :
#   name            - Nom affiché
#   symbol          - Caractère ASCII sur la carte
#   color           - Couleur RGB
#   hp_mult         - Multiplicateur de PV (base * hp_mult)
#   attack_mod      - Modificateur d'attaque (ajouté à la base)
#   defense_mod     - Modificateur de défense
#   speed           - Vitesse (pour l'IA future)
#   group_size      - (min, max) ennemis par groupe
#   floor_peak      - Étage de probabilité maximale
#   probability_range - (étage_min, étage_max) où la race peut apparaître

RACES = [
    # ============================================================
    # TIER 1 : VERMINES ET CRÉATURES FAIBLES (pic étages 1-20)
    # ============================================================
    {
        "name": "Vase",
        "symbol": "j",
        "color": (80, 220, 80),
        "hp_mult": 0.4,
        "attack_mod": -2,
        "defense_mod": 0,
        "speed": 1,
        "group_size": (3, 6),
        "floor_peak": 5,
        "probability_range": (1, 40),
    },
    {
        "name": "Vermine",
        "symbol": "r",
        "color": (160, 120, 80),
        "hp_mult": 0.4,
        "attack_mod": -1,
        "defense_mod": 0,
        "speed": 3,
        "group_size": (3, 5),
        "floor_peak": 7,
        "probability_range": (1, 35),
    },
    {
        "name": "Gobelin",
        "symbol": "g",
        "color": (60, 160, 60),
        "hp_mult": 0.6,
        "attack_mod": 0,
        "defense_mod": 0,
        "speed": 2,
        "group_size": (2, 4),
        "floor_peak": 10,
        "probability_range": (1, 45),
    },
    {
        "name": "Kobold",
        "symbol": "k",
        "color": (200, 140, 60),
        "hp_mult": 0.5,
        "attack_mod": 0,
        "defense_mod": 1,
        "speed": 2,
        "group_size": (2, 4),
        "floor_peak": 12,
        "probability_range": (1, 48),
    },
    {
        "name": "Tisseuse d'Ombre",
        "symbol": "x",
        "color": (120, 40, 80),
        "hp_mult": 0.5,
        "attack_mod": 1,
        "defense_mod": 0,
        "speed": 3,
        "group_size": (2, 4),
        "floor_peak": 15,
        "probability_range": (1, 50),
    },
    {
        "name": "Mycelide",
        "symbol": "m",
        "color": (180, 100, 220),
        "hp_mult": 0.7,
        "attack_mod": -1,
        "defense_mod": 2,
        "speed": 1,
        "group_size": (2, 4),
        "floor_peak": 13,
        "probability_range": (1, 48),
    },
    {
        "name": "Flamme Errante",
        "symbol": "*",
        "color": (100, 220, 255),
        "hp_mult": 0.3,
        "attack_mod": 2,
        "defense_mod": 0,
        "speed": 4,
        "group_size": (2, 3),
        "floor_peak": 18,
        "probability_range": (1, 52),
    },

    # ============================================================
    # TIER 2 : HUMANOÏDES ET MORTS-VIVANTS (pic étages 20-35)
    # ============================================================
    {
        "name": "Squelette",
        "symbol": "s",
        "color": (220, 220, 200),
        "hp_mult": 0.7,
        "attack_mod": 1,
        "defense_mod": 1,
        "speed": 2,
        "group_size": (2, 4),
        "floor_peak": 22,
        "probability_range": (5, 58),
    },
    {
        "name": "Orc",
        "symbol": "o",
        "color": (100, 140, 60),
        "hp_mult": 1.0,
        "attack_mod": 2,
        "defense_mod": 1,
        "speed": 2,
        "group_size": (1, 3),
        "floor_peak": 25,
        "probability_range": (8, 60),
    },
    {
        "name": "Gnoll",
        "symbol": "G",
        "color": (180, 150, 80),
        "hp_mult": 0.8,
        "attack_mod": 3,
        "defense_mod": 0,
        "speed": 3,
        "group_size": (2, 4),
        "floor_peak": 28,
        "probability_range": (10, 62),
    },
    {
        "name": "Harpie",
        "symbol": "h",
        "color": (220, 150, 200),
        "hp_mult": 0.6,
        "attack_mod": 3,
        "defense_mod": 0,
        "speed": 4,
        "group_size": (1, 3),
        "floor_peak": 30,
        "probability_range": (12, 65),
    },
    {
        "name": "Homme-Lezard",
        "symbol": "l",
        "color": (60, 180, 140),
        "hp_mult": 0.9,
        "attack_mod": 2,
        "defense_mod": 2,
        "speed": 2,
        "group_size": (2, 3),
        "floor_peak": 33,
        "probability_range": (15, 68),
    },

    # ============================================================
    # TIER 3 : CRÉATURES DANGEREUSES (pic étages 35-55)
    # ============================================================
    {
        "name": "Troll",
        "symbol": "T",
        "color": (80, 130, 60),
        "hp_mult": 1.8,
        "attack_mod": 3,
        "defense_mod": 2,
        "speed": 1,
        "group_size": (1, 2),
        "floor_peak": 38,
        "probability_range": (18, 72),
    },
    {
        "name": "Elementaire",
        "symbol": "E",
        "color": (120, 180, 255),
        "hp_mult": 1.2,
        "attack_mod": 4,
        "defense_mod": 1,
        "speed": 2,
        "group_size": (1, 2),
        "floor_peak": 42,
        "probability_range": (20, 75),
    },
    {
        "name": "Minotaure",
        "symbol": "M",
        "color": (160, 100, 60),
        "hp_mult": 2.0,
        "attack_mod": 5,
        "defense_mod": 3,
        "speed": 2,
        "group_size": (1, 1),
        "floor_peak": 45,
        "probability_range": (22, 78),
    },
    {
        "name": "Spectre",
        "symbol": "S",
        "color": (180, 180, 255),
        "hp_mult": 0.8,
        "attack_mod": 5,
        "defense_mod": 0,
        "speed": 3,
        "group_size": (1, 3),
        "floor_peak": 48,
        "probability_range": (22, 80),
    },
    {
        "name": "Naga",
        "symbol": "N",
        "color": (60, 200, 180),
        "hp_mult": 1.3,
        "attack_mod": 4,
        "defense_mod": 2,
        "speed": 2,
        "group_size": (1, 2),
        "floor_peak": 50,
        "probability_range": (25, 82),
    },
    {
        "name": "Golem de Pierre",
        "symbol": "W",
        "color": (150, 150, 150),
        "hp_mult": 2.5,
        "attack_mod": 2,
        "defense_mod": 6,
        "speed": 1,
        "group_size": (1, 1),
        "floor_peak": 53,
        "probability_range": (28, 82),
    },

    # ============================================================
    # TIER 4 : CRÉATURES REDOUTABLES (pic étages 55-75)
    # ============================================================
    {
        "name": "Vampire",
        "symbol": "V",
        "color": (200, 50, 50),
        "hp_mult": 1.2,
        "attack_mod": 6,
        "defense_mod": 3,
        "speed": 4,
        "group_size": (1, 2),
        "floor_peak": 58,
        "probability_range": (30, 88),
    },
    {
        "name": "Diablotine",
        "symbol": "d",
        "color": (220, 60, 40),
        "hp_mult": 1.5,
        "attack_mod": 6,
        "defense_mod": 3,
        "speed": 2,
        "group_size": (1, 3),
        "floor_peak": 62,
        "probability_range": (30, 90),
    },
    {
        "name": "Wendigo",
        "symbol": "w",
        "color": (180, 220, 255),
        "hp_mult": 1.8,
        "attack_mod": 8,
        "defense_mod": 2,
        "speed": 3,
        "group_size": (1, 1),
        "floor_peak": 65,
        "probability_range": (35, 92),
    },
    {
        "name": "Chimere",
        "symbol": "C",
        "color": (220, 200, 80),
        "hp_mult": 2.0,
        "attack_mod": 7,
        "defense_mod": 4,
        "speed": 2,
        "group_size": (1, 1),
        "floor_peak": 68,
        "probability_range": (35, 92),
    },
    {
        "name": "Gargouille",
        "symbol": "R",
        "color": (130, 130, 140),
        "hp_mult": 2.2,
        "attack_mod": 5,
        "defense_mod": 7,
        "speed": 1,
        "group_size": (1, 2),
        "floor_peak": 72,
        "probability_range": (35, 95),
    },

    # ============================================================
    # TIER 5 : CRÉATURES LÉGENDAIRES (pic étages 75-100)
    # Micro-chance dès l'étage 1, montent progressivement
    # ============================================================
    {
        "name": "Liche",
        "symbol": "Z",
        "color": (160, 255, 160),
        "hp_mult": 1.5,
        "attack_mod": 10,
        "defense_mod": 4,
        "speed": 2,
        "group_size": (1, 1),
        "floor_peak": 82,
        "probability_range": (1, 100),
    },
    {
        "name": "Dragon",
        "symbol": "D",
        "color": (255, 80, 20),
        "hp_mult": 4.0,
        "attack_mod": 15,
        "defense_mod": 10,
        "speed": 3,
        "group_size": (1, 1),
        "floor_peak": 95,
        "probability_range": (1, 100),
    },
]


# ==========================================
# 10 CLASSES GÉNÉRIQUES
# ==========================================
#
# Chaque classe définit :
#   name         - Nom affiché
#   description  - Capacité / comportement
#   hp_mult      - Multiplicateur de PV (appliqué après la race)
#   attack_mod   - Modificateur d'attaque
#   defense_mod  - Modificateur de défense

CLASSES = [
    {
        "name": "Guerrier",
        "description": "Combattant equilibre au corps a corps",
        "hp_mult": 1.0,
        "attack_mod": 2,
        "defense_mod": 2,
    },
    {
        "name": "Mage",
        "description": "Lanceur de sorts puissant mais fragile",
        "hp_mult": 0.8,
        "attack_mod": 5,
        "defense_mod": -1,
    },
    {
        "name": "Archer",
        "description": "Combattant a distance precis et rapide",
        "hp_mult": 0.9,
        "attack_mod": 3,
        "defense_mod": 0,
    },
    {
        "name": "Tank",
        "description": "Mur vivant, encaisse les coups pour les autres",
        "hp_mult": 1.4,
        "attack_mod": -1,
        "defense_mod": 5,
    },
    {
        "name": "Assassin",
        "description": "Frappe mortelle depuis les ombres",
        "hp_mult": 0.7,
        "attack_mod": 6,
        "defense_mod": -2,
    },
    {
        "name": "Pretre",
        "description": "Soigneur et protecteur divin",
        "hp_mult": 1.1,
        "attack_mod": 0,
        "defense_mod": 3,
    },
    {
        "name": "Berserker",
        "description": "Fureur incontrôlable, ignore la douleur",
        "hp_mult": 1.0,
        "attack_mod": 8,
        "defense_mod": -3,
    },
    {
        "name": "Necromancien",
        "description": "Magie noire et invocations de morts-vivants",
        "hp_mult": 0.9,
        "attack_mod": 4,
        "defense_mod": 0,
    },
    {
        "name": "Eclaireur",
        "description": "Rapide et agile, specialiste en reconnaissance",
        "hp_mult": 0.9,
        "attack_mod": 1,
        "defense_mod": 1,
    },
    {
        "name": "Champion",
        "description": "Elite parmi les combattants, stats superieures",
        "hp_mult": 1.2,
        "attack_mod": 4,
        "defense_mod": 3,
    },
]


# ==========================================
# FONCTIONS DE PROBABILITÉ
# ==========================================

def get_race_probability(race, floor):
    """
    Calcule la probabilité d'apparition d'une race à un étage donné.
    Utilise une courbe gaussienne centrée sur floor_peak.

    Args:
        race: Dictionnaire de la race
        floor: Numéro de l'étage (1-100)

    Returns:
        Probabilité entre 0.0 et 1.0
    """
    min_floor, max_floor = race["probability_range"]
    peak = race["floor_peak"]

    # Hors de la plage → probabilité nulle
    if floor < min_floor or floor > max_floor:
        return 0.0

    # Sigma basé sur la largeur de la plage (95% dans la plage)
    range_width = max_floor - min_floor
    sigma = range_width / 4.0

    if sigma == 0:
        return 1.0 if floor == peak else 0.0

    # Courbe gaussienne : max=1.0 au pic, décroît exponentiellement
    probability = math.exp(-0.5 * ((floor - peak) / sigma) ** 2)

    return probability


def select_floor_pool(floor, num_races_range=(3, 5)):
    """
    Sélectionne le pool de races disponibles pour un étage.
    Retourne 3 à 5 races avec leurs poids de probabilité.

    Args:
        floor: Numéro de l'étage (1-100)
        num_races_range: (min, max) races à sélectionner

    Returns:
        Liste de tuples (race, poids)
    """
    # Calculer les probabilités de toutes les races
    weighted_races = []
    for race in RACES:
        prob = get_race_probability(race, floor)
        if prob > 0.001:  # Seuil minimum pour éviter le bruit
            weighted_races.append((race, prob))

    if not weighted_races:
        # Fallback : prendre les Gobelins
        return [(RACES[2], 1.0)]

    # Nombre de races à sélectionner
    num_to_select = random.randint(num_races_range[0], num_races_range[1])
    num_to_select = min(num_to_select, len(weighted_races))

    # Sélection pondérée sans remplacement
    selected = []
    remaining = list(weighted_races)

    for _ in range(num_to_select):
        if not remaining:
            break

        total_weight = sum(w for _, w in remaining)
        r = random.uniform(0, total_weight)
        cumulative = 0

        for i, (race, weight) in enumerate(remaining):
            cumulative += weight
            if r <= cumulative:
                selected.append((race, weight))
                remaining.pop(i)
                break

    return selected


def create_enemy(race, enemy_class, floor, x, y):
    """
    Crée un ennemi avec les stats combinées de sa race, classe et étage.

    Stats finales :
        HP      = base_hp * race.hp_mult * class.hp_mult
        Attaque = base_attack + race.attack_mod + class.attack_mod
        Défense = race.defense_mod + class.defense_mod

    Args:
        race: Dictionnaire de la race
        enemy_class: Dictionnaire de la classe
        floor: Numéro de l'étage
        x, y: Position sur la carte

    Returns:
        Dictionnaire de l'ennemi (compatible avec le système existant)
    """
    # Stats de base selon l'étage (formule existante)
    base_hp = 30 + (floor - 1) * 5
    base_attack = 5 + (floor - 1) * 1

    # Appliquer les modificateurs race + classe
    final_hp = int(base_hp * race["hp_mult"] * enemy_class["hp_mult"])
    final_attack = base_attack + race["attack_mod"] + enemy_class["attack_mod"]
    final_defense = race["defense_mod"] + enemy_class["defense_mod"]

    # Minimum garanti
    final_hp = max(final_hp, 1)
    final_attack = max(final_attack, 1)
    final_defense = max(final_defense, 0)

    # Nom composé : "Race Classe"
    name = f"{race['name']} {enemy_class['name']}"

    return {
        "x": x,
        "y": y,
        "hp": final_hp,
        "max_hp": final_hp,
        "attack": final_attack,
        "defense": final_defense,
        "speed": race["speed"],
        "symbol": race["symbol"],
        "color": race["color"],
        "name": name,
        "race": race["name"],
        "class_name": enemy_class["name"],
    }
