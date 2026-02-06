"""
Gestion du joueur et de sa vision
"""

# Dictionnaire du joueur (toutes ses stats)
player = {
    "x": 5,
    "y": 5,
    "hp": 100,
    "max_hp": 100,
    "mana": 50,
    "max_mana": 50,
    "attack": 10,
    "defense": 5,
    "hunger": 100,
    "max_hunger": 100
}


def calculate_visible_tiles(player_x, player_y, vision_radius):
    """
    Calcule quelles cases sont visibles autour du joueur
    Retourne une liste de tuples (x, y)
    """
    visible = []

    # On regarde toutes les cases dans un carré autour du joueur
    for y in range(player_y - vision_radius, player_y + vision_radius + 1):
        for x in range(player_x - vision_radius, player_x + vision_radius + 1):
            # Calculer la distance au joueur (théorème de Pythagore)
            distance = ((x - player_x)**2 + (y - player_y)**2) ** 0.5

            # Si assez proche, c'est visible
            if distance <= vision_radius:
                visible.append((x, y))

    return visible


def reset_player(first_room):
    """Réinitialise le joueur (au début ou après game over)"""
    global player

    player["hp"] = player["max_hp"]
    player["mana"] = player["max_mana"]
    player["attack"] = 10
    player["defense"] = 5
    player["hunger"] = player["max_hunger"]

    # Position dans la première salle
    if first_room:
        player["x"] = first_room["x"] + 1
        player["y"] = first_room["y"] + 1
    else:
        player["x"] = 5
        player["y"] = 5


def spawn_player_in_room(first_room):
    """Place le joueur dans une salle (début d'étage)"""
    global player

    if first_room:
        player["x"] = first_room["x"] + 1
        player["y"] = first_room["y"] + 1
    else:
        player["x"] = 5
        player["y"] = 5


def check_hunger():
    """Gère les effets de la faim - Retourne True si le joueur meurt"""
    global player

    if player["hunger"] <= 0:
        player["hunger"] = 0
        # Perdre des PV si affamé
        player["hp"] -= 1
        print("Vous mourez de faim ! -1 HP")
        return player["hp"] <= 0  # Retourne True si mort
    elif player["hunger"] > player["max_hunger"]:
        player["hunger"] = player["max_hunger"]

    return False  # Pas mort
