"""
Gestion des ennemis : spawn (races/classes/groupes) et IA
"""

import random
from races_and_classes import CLASSES, select_floor_pool, create_enemy

# ==========================================
# SPAWN DES ENNEMIS (système races/classes)
# ==========================================

def spawn_enemies(num_slots, rooms, current_floor):
    """
    Spawne des groupes d'ennemis dans les salles.

    Chaque "slot" = un groupe d'ennemis de la même race.
    La taille du groupe dépend de la race (group_size).

    Étapes :
        1. Sélectionner 3-5 races pour cet étage (courbe de probabilité)
        2. Pour chaque slot, choisir une race du pool (pondéré)
        3. Spawner le groupe complet dans la même salle
        4. Chaque ennemi du groupe reçoit une classe aléatoire

    Args:
        num_slots: Nombre de "slots" (groupes) à spawner
        rooms: Liste des salles du donjon
        current_floor: Étage actuel (1-100)

    Returns:
        Liste d'ennemis (dictionnaires compatibles avec le reste du code)
    """
    enemies = []

    if not rooms:
        return enemies

    # 1. Sélectionner le pool de races pour cet étage
    floor_pool = select_floor_pool(current_floor)

    if not floor_pool:
        return enemies

    # Séparer races et poids pour la sélection pondérée
    pool_races = [race for race, _ in floor_pool]
    pool_weights = [weight for _, weight in floor_pool]

    # Afficher le pool dans la console (debug)
    race_names = [r["name"] for r in pool_races]
    print(f"[Étage {current_floor}] Races disponibles : {', '.join(race_names)}")

    for _ in range(num_slots):
        # 2. Choisir une race dans le pool (pondéré)
        race = random.choices(pool_races, weights=pool_weights, k=1)[0]

        # 3. Déterminer la taille du groupe
        group_min, group_max = race["group_size"]
        group_size = random.randint(group_min, group_max)

        # 4. Choisir une salle pour tout le groupe
        room = random.choice(rooms)

        # 5. Spawner chaque ennemi du groupe dans cette salle
        for _ in range(group_size):
            enemy_class = random.choice(CLASSES)

            # Trouver une position libre (max 20 tentatives)
            for _attempt in range(20):
                x = random.randint(room["x"] + 1, room["x"] + room["w"] - 2)
                y = random.randint(room["y"] + 1, room["y"] + room["h"] - 2)

                if not any(e["x"] == x and e["y"] == y for e in enemies):
                    enemy = create_enemy(race, enemy_class, current_floor, x, y)
                    enemies.append(enemy)
                    break

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
