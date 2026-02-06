"""
Génération procédurale de donjons
Système de salles + couloirs
"""

import random

# Constantes de la carte (style DCSS : large donjon)
MAP_WIDTH = 80
MAP_HEIGHT = 70

def create_dungeon():
    """
    Génère un donjon complet avec salles et couloirs
    Returns: (game_map, rooms)
        - game_map: liste 2D de caractères
        - rooms: liste de dictionnaires {"x", "y", "w", "h"}
    """
    # 1. Créer une carte pleine de murs
    game_map = []
    for y in range(MAP_HEIGHT):
        row = []
        for x in range(MAP_WIDTH):
            row.append('#')
        game_map.append(row)

    # 2. Créer ~20 salles de tailles variées
    rooms = []
    num_rooms = random.randint(15, 25)

    for i in range(num_rooms):
        # Taille aléatoire : petites (4×4) à grandes (15×12)
        width = random.randint(4, 15)
        height = random.randint(4, 12)

        # Position aléatoire
        x = random.randint(1, MAP_WIDTH - width - 1)
        y = random.randint(1, MAP_HEIGHT - height - 1)

        # Créer la salle
        new_room = {"x": x, "y": y, "w": width, "h": height}

        # Vérifier qu'elle ne chevauche pas les autres
        can_place = True
        for other_room in rooms:
            if rooms_overlap(new_room, other_room):
                can_place = False
                break

        # Si OK, creuser la salle et l'ajouter
        if can_place:
            carve_room(game_map, new_room)
            rooms.append(new_room)

    # 3. Relier les salles avec des couloirs
    for i in range(len(rooms) - 1):
        room1 = rooms[i]
        room2 = rooms[i + 1]

        # Centre de chaque salle
        x1 = room1["x"] + room1["w"] // 2
        y1 = room1["y"] + room1["h"] // 2

        x2 = room2["x"] + room2["w"] // 2
        y2 = room2["y"] + room2["h"] // 2

        # Créer couloir en L
        create_h_corridor(game_map, x1, x2, y1)
        create_v_corridor(game_map, y1, y2, x2)

    # 4. Placer l'escalier dans la dernière salle
    if rooms:
        last_room = rooms[-1]
        stairs_x = last_room["x"] + last_room["w"] // 2
        stairs_y = last_room["y"] + last_room["h"] // 2
        game_map[stairs_y][stairs_x] = '>'

    return game_map, rooms


def carve_room(game_map, room):
    """Creuse une salle rectangulaire dans la carte"""
    for y in range(room["y"], room["y"] + room["h"]):
        for x in range(room["x"], room["x"] + room["w"]):
            game_map[y][x] = '.'


def rooms_overlap(room1, room2):
    """Vérifie si deux salles se chevauchent (avec marge de 1)"""
    return (room1["x"] < room2["x"] + room2["w"] + 1 and
            room1["x"] + room1["w"] + 1 > room2["x"] and
            room1["y"] < room2["y"] + room2["h"] + 1 and
            room1["y"] + room1["h"] + 1 > room2["y"])


def create_h_corridor(game_map, x1, x2, y):
    """Creuse un couloir horizontal"""
    for x in range(min(x1, x2), max(x1, x2) + 1):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            game_map[y][x] = '.'


def create_v_corridor(game_map, y1, y2, x):
    """Creuse un couloir vertical"""
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            game_map[y][x] = '.'


def get_room_center(room):
    """Retourne le centre d'une salle"""
    center_x = room["x"] + room["w"] // 2
    center_y = room["y"] + room["h"] // 2
    return center_x, center_y
