"""
Gestion des ennemis : spawn et IA
"""

import random

# ==========================================
# SPAWN DES ENNEMIS
# ==========================================

def spawn_enemies(num_enemies, rooms, current_floor):
    """
    Spawne des ennemis dans les salles

    Args:
        num_enemies: Nombre d'ennemis à créer
        rooms: Liste des salles du donjon
        current_floor: Étage actuel (pour calculer les stats)

    Returns:
        Liste d'ennemis
    """
    enemies = []

    # Calculer les stats selon l'étage
    base_hp = 30
    base_attack = 5

    enemy_hp = base_hp + (current_floor - 1) * 5
    enemy_attack = base_attack + (current_floor - 1) * 1

    for _ in range(num_enemies):
        if not rooms:  # Sécurité si pas de salles
            break

        # Choisir une salle au hasard
        room = random.choice(rooms)

        # Position aléatoire dans cette salle
        x = random.randint(room["x"] + 1, room["x"] + room["w"] - 2)
        y = random.randint(room["y"] + 1, room["y"] + room["h"] - 2)

        # Vérifier qu'il n'y a pas déjà un ennemi ici
        if not any(e["x"] == x and e["y"] == y for e in enemies):
            enemies.append({
                "x": x,
                "y": y,
                "hp": enemy_hp,
                "max_hp": enemy_hp,
                "attack": enemy_attack,
                "symbol": "e",
                "color": (255, 100, 100)
            })

    return enemies


def get_enemy_at(x, y, enemies):
    """
    Trouve un ennemi à la position (x, y)

    Args:
        x, y: Position à vérifier
        enemies: Liste des ennemis

    Returns:
        L'ennemi trouvé ou None
    """
    for enemy in enemies:
        if enemy["x"] == x and enemy["y"] == y:
            return enemy
    return None


# ==========================================
# IA DES ENNEMIS
# ==========================================

def enemy_turn(enemies, player, game_map):
    """
    Fait jouer tous les ennemis (un tour complet)

    Args:
        enemies: Liste des ennemis
        player: Le joueur
        game_map: La carte du donjon
    """
    for enemy in enemies:
        # Pour l'instant : IA simple (se rapprocher du joueur)
        move_towards_player(enemy, player, game_map, enemies)


def move_towards_player(enemy, player, game_map, enemies):
    """
    Déplace un ennemi vers le joueur (IA basique)

    Args:
        enemy: L'ennemi à déplacer
        player: Le joueur
        game_map: La carte
        enemies: Liste de tous les ennemis (pour éviter collisions)
    """
    # Calculer la distance au joueur
    distance = abs(enemy["x"] - player["x"]) + abs(enemy["y"] - player["y"])

    # Si trop loin, ne bouge pas (économise du calcul)
    if distance > 10:
        return

    # Calculer la direction vers le joueur
    dx = 0
    dy = 0

    if player["x"] > enemy["x"]:
        dx = 1
    elif player["x"] < enemy["x"]:
        dx = -1

    if player["y"] > enemy["y"]:
        dy = 1
    elif player["y"] < enemy["y"]:
        dy = -1

    # Essayer de bouger (priorité : horizontal puis vertical)
    # Essai 1 : Bouger horizontalement
    if dx != 0:
        new_x = enemy["x"] + dx
        new_y = enemy["y"]

        if can_enemy_move(new_x, new_y, game_map, enemies):
            enemy["x"] = new_x
            return

    # Essai 2 : Bouger verticalement
    if dy != 0:
        new_x = enemy["x"]
        new_y = enemy["y"] + dy

        if can_enemy_move(new_x, new_y, game_map, enemies):
            enemy["y"] = new_y
            return


def can_enemy_move(x, y, game_map, enemies):
    """
    Vérifie si un ennemi peut se déplacer à (x, y)

    Args:
        x, y: Position cible
        game_map: La carte
        enemies: Liste des ennemis

    Returns:
        True si la case est libre, False sinon
    """
    # Vérifier les limites de la carte
    if x < 0 or x >= len(game_map[0]) or y < 0 or y >= len(game_map):
        return False

    # Vérifier que c'est du sol
    if game_map[y][x] != '.':
        return False

    # Vérifier qu'il n'y a pas d'autre ennemi
    if get_enemy_at(x, y, enemies):
        return False

    return True
