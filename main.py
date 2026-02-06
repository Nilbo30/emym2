"""
Roguelike - Fichier principal
Boucle de jeu et coordination
"""

import pygame
import sys
from map_generation import create_dungeon, MAP_WIDTH, MAP_HEIGHT
from enemies import spawn_enemies, get_enemy_at, enemy_turn
from player import player, calculate_visible_tiles, reset_player, spawn_player_in_room, check_hunger, STEPS_PER_HUNGER
from rendering import (draw_map, draw_player, draw_enemies, draw_items, draw_ui,
                       set_visible_tiles, draw_inventory, draw_inventory_button,
                       draw_tooltip, draw_enemy_tooltip,
                       update_camera, get_camera, VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
from game_logic import get_item_at, pickup_item, combat, can_move
from items import spawn_items
from inventory import clear_inventory, print_inventory

# Initialisation de Pygame
pygame.init()

# Constantes
TILE_SIZE = 32
SCREEN_WIDTH = TILE_SIZE * VIEWPORT_WIDTH
SCREEN_HEIGHT = TILE_SIZE * VIEWPORT_HEIGHT
VISION_RADIUS = 9

BLACK = (0, 0, 0)

# Créer la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike - Etage 1")

# Police pour afficher les caractères ASCII
font = pygame.font.Font(None, TILE_SIZE)

# Variables globales du jeu
enemies = []
items = []
rooms = []
current_floor = 1
inventory_open = False
inventory_tab = "bag"  # "bag" ou "equip"
inventory_button_rect = (0, 0, 0, 0)
inventory_rects = None


def create_explored_map():
    """Crée un tableau pour se souvenir de ce qu'on a exploré"""
    explored = []
    for y in range(MAP_HEIGHT):
        row = []
        for x in range(MAP_WIDTH):
            row.append(False)
        explored.append(row)
    return explored


def descend_floor():
    """Descend d'un étage"""
    global current_floor, game_map, enemies, items, rooms, explored

    current_floor += 1
    game_map, rooms = create_dungeon()
    explored = create_explored_map()
    enemies = spawn_enemies(5, rooms, current_floor)
    items = spawn_items(5, rooms, game_map, MAP_WIDTH, MAP_HEIGHT, floor_level=current_floor)

    spawn_player_in_room(rooms[0] if rooms else None)

    pygame.display.set_caption(f"Roguelike - Etage {current_floor}")
    print(f"Vous descendez a l'etage {current_floor}!")


def game_over():
    """Game over - réinitialise le jeu"""
    global current_floor, game_map, enemies, items, rooms, explored, inventory_open, inventory_tab

    print("\n" + "="*50)
    print("GAME OVER !")
    print("="*50)
    print(f"Vous avez atteint l'etage {current_floor}")
    print("Nouvelle partie...\n")

    current_floor = 1
    game_map, rooms = create_dungeon()
    explored = create_explored_map()
    enemies = spawn_enemies(5, rooms, current_floor)
    items = spawn_items(5, rooms, game_map, MAP_WIDTH, MAP_HEIGHT, floor_level=current_floor)

    clear_inventory()
    reset_player(rooms[0] if rooms else None)
    inventory_open = False
    inventory_tab = "bag"

    pygame.display.set_caption("Roguelike - Etage 1")


# Créer la première carte
game_map, rooms = create_dungeon()
explored = create_explored_map()

# Placer le joueur dans la première salle
spawn_player_in_room(rooms[0] if rooms else None)

# Spawner ennemis et items
enemies = spawn_enemies(5, rooms, current_floor)
items = spawn_items(5, rooms, game_map, MAP_WIDTH, MAP_HEIGHT, floor_level=current_floor)


# ==========================================
# BOUCLE PRINCIPALE
# ==========================================

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Clics de souris
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Si l'inventaire est ouvert
            if inventory_open and inventory_rects:
                inv_x, inv_y, inv_width, inv_height = inventory_rects['window']
                btn_x, btn_y, btn_width, btn_height = inventory_rects['close_button']
                item_rects = inventory_rects.get('items', [])

                # Clic sur onglet Sac ?
                tx, ty, tw, th = inventory_rects.get('tab_bag', (0, 0, 0, 0))
                if tx <= mouse_x <= tx + tw and ty <= mouse_y <= ty + th:
                    inventory_tab = "bag"
                    continue

                # Clic sur onglet Équipement ?
                tx, ty, tw, th = inventory_rects.get('tab_equip', (0, 0, 0, 0))
                if tx <= mouse_x <= tx + tw and ty <= mouse_y <= ty + th:
                    inventory_tab = "equip"
                    continue

                # Clic sur un item ?
                clicked_item = None
                for item, (ix, iy, iw, ih) in item_rects:
                    if ix <= mouse_x <= ix + iw and iy <= mouse_y <= iy + ih:
                        clicked_item = item
                        break

                if clicked_item:
                    from game_logic import toggle_equip_item, consume_item

                    if clicked_item["type"] in ["weapon", "armor", "shield", "accessory"]:
                        toggle_equip_item(clicked_item)
                    elif clicked_item["type"] == "food":
                        consume_item(clicked_item)
                    continue

                # Clic sur bouton "Fermer" ?
                if btn_x <= mouse_x <= btn_x + btn_width:
                    if btn_y <= mouse_y <= btn_y + btn_height:
                        inventory_open = False
                        continue

                # Clic EN DEHORS de la fenêtre ?
                if not (inv_x <= mouse_x <= inv_x + inv_width and
                        inv_y <= mouse_y <= inv_y + inv_height):
                    inventory_open = False
                    continue

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
                continue
            # Tab pour changer d'onglet quand l'inventaire est ouvert
            if inventory_open and event.key == pygame.K_TAB:
                inventory_tab = "equip" if inventory_tab == "bag" else "bag"
                continue
            if inventory_open:
                continue  # Bloquer le mouvement si l'inventaire est ouvert

            new_x = player["x"]
            new_y = player["y"]

            if event.key == pygame.K_UP:
                new_y -= 1
            elif event.key == pygame.K_DOWN:
                new_y += 1
            elif event.key == pygame.K_LEFT:
                new_x -= 1
            elif event.key == pygame.K_RIGHT:
                new_x += 1
            else:
                continue

            # Vérifier s'il y a un ennemi sur la case cible
            enemy_at_target = get_enemy_at(new_x, new_y, enemies)

            if enemy_at_target:
                player_died = combat(enemy_at_target, enemies)
                if player_died:
                    game_over()
                else:
                    enemy_turn(enemies, player, game_map)

            elif can_move(new_x, new_y, game_map, MAP_WIDTH, MAP_HEIGHT):
                player["x"] = new_x
                player["y"] = new_y

                # La faim diminue tous les STEPS_PER_HUNGER pas
                player["step_counter"] += 1
                if player["step_counter"] >= STEPS_PER_HUNGER:
                    player["step_counter"] = 0
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

                # Tour des ennemis
                enemy_turn(enemies, player, game_map)

    # Calculer ce qui est visible
    visible_tiles = calculate_visible_tiles(player["x"], player["y"], VISION_RADIUS)
    set_visible_tiles(visible_tiles)

    # Mettre à jour la mémoire
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

    # Tooltip d'ennemi (seulement si inventaire fermé)
    if not inventory_open:
        cam_x, cam_y = get_camera()
        grid_x = cam_x + mouse_x // TILE_SIZE
        grid_y = cam_y + mouse_y // TILE_SIZE

        for enemy in enemies:
            if enemy["x"] == grid_x and enemy["y"] == grid_y:
                visible_tiles_check = calculate_visible_tiles(player["x"], player["y"], VISION_RADIUS)
                if (enemy["x"], enemy["y"]) in visible_tiles_check:
                    hovered_enemy = enemy
                    break

        # Tooltip d'item au sol
        if not hovered_enemy:
            for item in items:
                if item["x"] == grid_x and item["y"] == grid_y:
                    if (item["x"], item["y"]) in visible_tiles:
                        hovered_item = item
                        break

    # Mettre à jour la caméra
    update_camera(player["x"], player["y"], MAP_WIDTH, MAP_HEIGHT)

    # Effacer l'écran
    screen.fill(BLACK)

    # Dessiner tout
    draw_map(screen, game_map, explored, font, TILE_SIZE, MAP_HEIGHT, MAP_WIDTH)
    draw_items(screen, items, font, TILE_SIZE)
    draw_enemies(screen, enemies, font, TILE_SIZE)
    draw_player(screen, player, font, TILE_SIZE)
    draw_ui(screen, player, current_floor, SCREEN_WIDTH)

    # Bouton inventaire
    inventory_button_rect = draw_inventory_button(screen, SCREEN_WIDTH, inventory_open)

    # Inventaire par-dessus si ouvert
    if inventory_open:
        from inventory import get_inventory
        inventory_rects = draw_inventory(screen, get_inventory(), SCREEN_WIDTH, SCREEN_HEIGHT, active_tab=inventory_tab)
    else:
        inventory_rects = None

    # Tooltips
    if hovered_item:
        draw_tooltip(screen, hovered_item, mouse_x, mouse_y, SCREEN_WIDTH, SCREEN_HEIGHT)

    if hovered_enemy:
        draw_enemy_tooltip(screen, hovered_enemy, mouse_x, mouse_y, SCREEN_WIDTH, SCREEN_HEIGHT)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
