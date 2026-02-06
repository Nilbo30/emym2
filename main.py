"""
Roguelike - Fichier principal
Boucle de jeu et coordination
"""

import pygame
import sys
from map_generation import create_dungeon
from enemies import spawn_enemies, get_enemy_at, enemy_turn
from player import player, calculate_visible_tiles, reset_player, spawn_player_in_room, check_hunger
from rendering import draw_map, draw_player, draw_enemies, draw_items, draw_ui, set_visible_tiles, draw_inventory, draw_inventory_button, draw_tooltip, draw_enemy_tooltip
from game_logic import get_item_at, pickup_item, combat, spawn_items, can_move
from inventory import clear_inventory, print_inventory

# Initialisation de Pygame
pygame.init()

# Constantes
TILE_SIZE = 32
MAP_WIDTH = 25
MAP_HEIGHT = 20
SCREEN_WIDTH = TILE_SIZE * MAP_WIDTH
SCREEN_HEIGHT = TILE_SIZE * MAP_HEIGHT
VISION_RADIUS = 6

# Couleurs
BLACK = (0, 0, 0)

# Créer la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike - Étage 1")

# Police pour afficher les caractères ASCII
font = pygame.font.Font(None, TILE_SIZE)

# Variables globales du jeu
enemies = []
items = []
rooms = []
current_floor = 1
inventory_open = False
inventory_button_rect = (0, 0, 0, 0)
inventory_rects = None


def create_explored_map():
    """Crée un tableau pour se souvenir de ce qu'on a exploré"""
    explored = []
    for y in range(MAP_HEIGHT):
        row = []
        for x in range(MAP_WIDTH):
            row.append(False)  # False = jamais vu
        explored.append(row)
    return explored


def descend_floor():
    """Descend d'un étage"""
    global current_floor, game_map, enemies, items, rooms, explored

    current_floor += 1
    game_map, rooms = create_dungeon()
    explored = create_explored_map()
    enemies = spawn_enemies(5, rooms, current_floor)
    items = spawn_items(3, rooms, game_map, MAP_WIDTH, MAP_HEIGHT)

    spawn_player_in_room(rooms[0] if rooms else None)

    pygame.display.set_caption(f"Roguelike - Étage {current_floor}")
    print(f"Vous descendez à l'étage {current_floor}!")


def game_over():
    """Game over - réinitialise le jeu"""
    global current_floor, game_map, enemies, items, rooms, explored

    print("\n" + "="*50)
    print("GAME OVER !")
    print("="*50)
    print(f"Vous avez atteint l'étage {current_floor}")
    print("Nouvelle partie...\n")

    # Réinitialiser
    current_floor = 1
    game_map, rooms = create_dungeon()
    explored = create_explored_map()
    enemies = spawn_enemies(5, rooms, current_floor)
    items = spawn_items(3, rooms, game_map, MAP_WIDTH, MAP_HEIGHT)

    clear_inventory()

    reset_player(rooms[0] if rooms else None)

    pygame.display.set_caption("Roguelike - Étage 1")


# Créer la première carte
game_map, rooms = create_dungeon()
explored = create_explored_map()

# Placer le joueur dans la première salle
spawn_player_in_room(rooms[0] if rooms else None)

# Spawner ennemis et items
enemies = spawn_enemies(5, rooms, current_floor)
items = spawn_items(3, rooms, game_map, MAP_WIDTH, MAP_HEIGHT)


# ==========================================
# BOUCLE PRINCIPALE
# ==========================================

clock = pygame.time.Clock()
running = True

while running:
    # Gérer les événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

       # Détecter les clics de souris
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Si l'inventaire est ouvert
            if inventory_open and inventory_rects:
                # Coordonnées de la fenêtre d'inventaire
                inv_x, inv_y, inv_width, inv_height = inventory_rects['window']
                btn_x, btn_y, btn_width, btn_height = inventory_rects['close_button']
                item_rects = inventory_rects.get('items', [])

                # Clic sur un item ?
                clicked_item = None
                for item, (ix, iy, iw, ih) in item_rects:
                    if ix <= mouse_x <= ix + iw and iy <= mouse_y <= iy + ih:
                        clicked_item = item
                        break

                if clicked_item:
                    # Action selon le type d'item
                    from game_logic import toggle_equip_item, consume_item

                    if clicked_item["type"] in ["weapon", "armor"]:
                        toggle_equip_item(clicked_item)
                    elif clicked_item["type"] == "food":
                        consume_item(clicked_item)

                    continue  # Ne pas traiter d'autres clics

                # Clic sur le bouton "Fermer" ?
                if btn_x <= mouse_x <= btn_x + btn_width:
                    if btn_y <= mouse_y <= btn_y + btn_height:
                        inventory_open = False
                        continue

                # Clic EN DEHORS de la fenêtre d'inventaire ?
                if not (inv_x <= mouse_x <= inv_x + inv_width and
                        inv_y <= mouse_y <= inv_y + inv_height):
                    inventory_open = False
                    continue

                # Clic DANS la fenêtre mais pas sur un item ou bouton = ne rien faire
                continue

            # Si l'inventaire est fermé, vérifier le bouton d'ouverture
            else:
                button_x, button_y, button_width, button_height = inventory_button_rect

                if button_x <= mouse_x <= button_x + button_width:
                    if button_y <= mouse_y <= button_y + button_height:
                        inventory_open = not inventory_open

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                inventory_open = not inventory_open
                continue  # Ne pas traiter comme un mouvement
            if inventory_open:
                continue  # Bloquer le mouvement si l'inventaire est ouvert
            new_x = player["x"]
            new_y = player["y"]

            # Déterminer la direction
            if event.key == pygame.K_UP:
                new_y -= 1
            elif event.key == pygame.K_DOWN:
                new_y += 1
            elif event.key == pygame.K_LEFT:
                new_x -= 1
            elif event.key == pygame.K_RIGHT:
                new_x += 1
            else:
                continue  # Touche non gérée



            # Vérifier s'il y a un ennemi sur la case cible
            enemy_at_target = get_enemy_at(new_x, new_y, enemies)

            if enemy_at_target:
                # Combat !
                player_died = combat(enemy_at_target, enemies)
                if player_died:
                    game_over()
                else:
                    # Tour des ennemis après le combat
                    enemy_turn(enemies, player, game_map)

            elif can_move(new_x, new_y, game_map, MAP_WIDTH, MAP_HEIGHT):
                # Déplacement
                player["x"] = new_x
                player["y"] = new_y

                # La faim diminue en se déplaçant
                player["hunger"] -= 1
                if check_hunger():
                    game_over()
                    continue

                # Vérifier s'il y a un objet à ramasser
                item_at_position = get_item_at(player["x"], player["y"], items)
                if item_at_position:
                    pickup_item(item_at_position, items)

                # Vérifier escalier
                if game_map[player["y"]][player["x"]] == '>':
                    descend_floor()

                # Tour des ennemis après le mouvement
                enemy_turn(enemies, player, game_map)

    # Calculer ce qui est visible
    visible_tiles = calculate_visible_tiles(player["x"], player["y"], VISION_RADIUS)
    set_visible_tiles(visible_tiles)  # Envoyer à rendering.py

    # Mettre à jour la mémoire (marquer comme exploré)
    for (x, y) in visible_tiles:
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            explored[y][x] = True

    # Détecter le survol de souris (pour les tooltips)
    hovered_item = None
    hovered_enemy = None
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Tooltip d'inventaire (seulement si ouvert)
    if inventory_open and inventory_rects:
        item_rects = inventory_rects.get('items', [])

        for item, (ix, iy, iw, ih) in item_rects:
            if ix <= mouse_x <= ix + iw and iy <= mouse_y <= iy + ih:
                hovered_item = item
                break

    # Tooltip d'ennemi (seulement si inventaire FERMÉ)
    if not inventory_open:
        # Convertir position souris en position grille
        grid_x = mouse_x // TILE_SIZE
        grid_y = mouse_y // TILE_SIZE

        # Vérifier s'il y a un ennemi à cette position
        for enemy in enemies:
            if enemy["x"] == grid_x and enemy["y"] == grid_y:
                # Vérifier que l'ennemi est visible
                visible_tiles = calculate_visible_tiles(player["x"], player["y"], VISION_RADIUS)
                if (enemy["x"], enemy["y"]) in visible_tiles:
                    hovered_enemy = enemy
                    break

    # Effacer l'écran
    screen.fill(BLACK)

    # Dessiner tout
    draw_map(screen, game_map, explored, font, TILE_SIZE, MAP_HEIGHT, MAP_WIDTH)
    draw_items(screen, items, font, TILE_SIZE)
    draw_enemies(screen, enemies, font, TILE_SIZE)
    draw_player(screen, player, font, TILE_SIZE)
    draw_ui(screen, player, current_floor, SCREEN_WIDTH)

    # Dessiner le bouton inventaire et récupérer ses coordonnées
    inventory_button_rect = draw_inventory_button(screen, SCREEN_WIDTH, inventory_open)

    # Dessiner l'inventaire par-dessus si ouvert
    if inventory_open:
        from inventory import get_inventory
        inventory_rects = draw_inventory(screen, get_inventory(), SCREEN_WIDTH, SCREEN_HEIGHT)
    else:
        inventory_rects = None

    # Dessiner les tooltips
    if hovered_item:
        draw_tooltip(screen, hovered_item, mouse_x, mouse_y, SCREEN_WIDTH, SCREEN_HEIGHT)

    if hovered_enemy:
        draw_enemy_tooltip(screen, hovered_enemy, mouse_x, mouse_y, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Limiter à 60 FPS
    clock.tick(60)

# Quitter proprement
pygame.quit()
sys.exit()
