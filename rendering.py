"""
Fonctions d'affichage / rendu graphique
Système de caméra centrée sur le joueur (style DCSS)
"""

import pygame

# ==========================================
# CONSTANTES DU VIEWPORT
# ==========================================

VIEWPORT_WIDTH = 35   # Cases affichées en largeur
VIEWPORT_HEIGHT = 17  # Cases affichées en hauteur

# ==========================================
# VARIABLES GLOBALES
# ==========================================

visible_tiles = set()  # Set pour O(1) lookup
camera_x = 0
camera_y = 0


# ==========================================
# CAMÉRA
# ==========================================

def update_camera(player_x, player_y, map_width, map_height):
    """
    Centre la caméra sur le joueur.
    Bloque aux bords pour ne pas montrer hors de la carte.
    """
    global camera_x, camera_y
    camera_x = player_x - VIEWPORT_WIDTH // 2
    camera_y = player_y - VIEWPORT_HEIGHT // 2

    # Clamper aux limites de la carte
    camera_x = max(0, min(camera_x, map_width - VIEWPORT_WIDTH))
    camera_y = max(0, min(camera_y, map_height - VIEWPORT_HEIGHT))


def get_camera():
    """Retourne la position actuelle de la caméra (pour main.py)"""
    return camera_x, camera_y


def set_visible_tiles(tiles):
    """Met à jour les cases visibles (converties en set pour performance)"""
    global visible_tiles
    visible_tiles = set(tiles)


# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================

def _world_to_screen(world_x, world_y, tile_size):
    """Convertit des coordonnées monde en pixels écran"""
    return (world_x - camera_x) * tile_size, (world_y - camera_y) * tile_size


def _is_on_screen(world_x, world_y):
    """Vérifie si une position monde est dans le viewport"""
    vx = world_x - camera_x
    vy = world_y - camera_y
    return 0 <= vx < VIEWPORT_WIDTH and 0 <= vy < VIEWPORT_HEIGHT


# ==========================================
# DESSIN DE LA CARTE (avec caméra + fog of war)
# ==========================================

def draw_map(screen, game_map, explored, font, TILE_SIZE, MAP_HEIGHT, MAP_WIDTH):
    """
    Dessine la portion visible de la carte avec fog of war.

    3 états par case :
    - Non explorée : noir total (rien affiché)
    - Explorée mais hors vision : gris foncé (structure visible, pas les entités)
    - Visible (dans le rayon du joueur) : couleurs complètes
    """
    for vy in range(VIEWPORT_HEIGHT):
        for vx in range(VIEWPORT_WIDTH):
            # Coordonnées monde
            wx = camera_x + vx
            wy = camera_y + vy

            # Hors limites de la carte
            if wx < 0 or wx >= MAP_WIDTH or wy < 0 or wy >= MAP_HEIGHT:
                continue

            tile = game_map[wy][wx]
            is_visible = (wx, wy) in visible_tiles
            is_explored = explored[wy][wx]

            # Non exploré = noir total
            if not is_explored:
                continue

            # Position en pixels sur l'écran
            sx = vx * TILE_SIZE
            sy = vy * TILE_SIZE

            # Couleurs selon l'état de visibilité
            if is_visible:
                # Visible : couleurs complètes
                if tile == '#':
                    color = (128, 128, 128)    # Mur gris
                elif tile == '.':
                    color = (30, 30, 35)       # Sol légèrement visible
                elif tile == '>':
                    color = (255, 255, 0)      # Escalier jaune vif
                else:
                    color = (255, 255, 255)
            else:
                # Exploré mais hors vision : gris foncé
                if tile == '#':
                    color = (50, 50, 55)       # Mur sombre
                elif tile == '.':
                    color = (18, 18, 22)       # Sol très sombre
                elif tile == '>':
                    color = (80, 80, 0)        # Escalier sombre
                else:
                    color = (40, 40, 40)

            # Dessiner le sol (rect)
            if tile == '.' or tile == '>':
                pygame.draw.rect(screen, color, (sx, sy, TILE_SIZE, TILE_SIZE))

            # Dessiner les caractères (murs, escaliers)
            if tile != '.':
                text = font.render(tile, True, color)
                text_rect = text.get_rect(center=(sx + TILE_SIZE // 2,
                                                   sy + TILE_SIZE // 2))
                screen.blit(text, text_rect)


# ==========================================
# DESSIN DES ENTITÉS (avec offset caméra)
# ==========================================

def draw_player(screen, player, font, TILE_SIZE):
    """Dessine le joueur (@) à sa position relative à la caméra"""
    if not _is_on_screen(player["x"], player["y"]):
        return

    sx, sy = _world_to_screen(player["x"], player["y"], TILE_SIZE)
    GREEN = (0, 255, 0)
    text = font.render('@', True, GREEN)
    text_rect = text.get_rect(center=(sx + TILE_SIZE // 2,
                                      sy + TILE_SIZE // 2))
    screen.blit(text, text_rect)


def draw_enemies(screen, enemies, font, TILE_SIZE):
    """Dessine les ennemis visibles dans le viewport"""
    for enemy in enemies:
        # Seulement si visible ET dans le viewport
        if (enemy["x"], enemy["y"]) not in visible_tiles:
            continue
        if not _is_on_screen(enemy["x"], enemy["y"]):
            continue

        sx, sy = _world_to_screen(enemy["x"], enemy["y"], TILE_SIZE)
        text = font.render(enemy["symbol"], True, enemy["color"])
        text_rect = text.get_rect(center=(sx + TILE_SIZE // 2,
                                          sy + TILE_SIZE // 2))
        screen.blit(text, text_rect)


def draw_items(screen, items, font, TILE_SIZE):
    """Dessine les objets visibles dans le viewport"""
    for item in items:
        # Seulement si visible ET dans le viewport
        if (item["x"], item["y"]) not in visible_tiles:
            continue
        if not _is_on_screen(item["x"], item["y"]):
            continue

        sx, sy = _world_to_screen(item["x"], item["y"], TILE_SIZE)
        text = font.render(item["symbol"], True, item["color"])
        text_rect = text.get_rect(center=(sx + TILE_SIZE // 2,
                                          sy + TILE_SIZE // 2))
        screen.blit(text, text_rect)


# ==========================================
# INTERFACE UTILISATEUR (positions fixes sur l'écran)
# ==========================================

def draw_ui(screen, player, current_floor, SCREEN_WIDTH):
    """Dessine l'interface utilisateur (stats, étage)"""
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)

    ui_font = pygame.font.Font(None, 24)

    # Afficher les PV
    hp_text = ui_font.render(f"PV: {player['hp']}/{player['max_hp']}", True, WHITE)
    screen.blit(hp_text, (10, 10))

    # Afficher le mana
    mana_text = ui_font.render(f"Mana: {player['mana']}/{player['max_mana']}", True, WHITE)
    screen.blit(mana_text, (10, 35))

    # Afficher l'étage
    floor_text = ui_font.render(f"Étage: {current_floor}", True, YELLOW)
    screen.blit(floor_text, (SCREEN_WIDTH - 120, 10))

    # Afficher attaque et défense
    stats_text = ui_font.render(f"ATK: {player['attack']}  DEF: {player['defense']}", True, WHITE)
    screen.blit(stats_text, (10, 60))

    # Afficher la faim
    if player['hunger'] > 50:
        hunger_color = GREEN
    elif player['hunger'] > 20:
        hunger_color = YELLOW
    else:
        hunger_color = (255, 0, 0)

    hunger_text = ui_font.render(f"Faim: {player['hunger']}/{player['max_hunger']}", True, hunger_color)
    screen.blit(hunger_text, (10, 85))


# ==========================================
# INVENTAIRE (popup centré, coordonnées écran fixes)
# ==========================================

def draw_inventory(screen, inventory, SCREEN_WIDTH, SCREEN_HEIGHT):
    """Dessine l'inventaire par-dessus le jeu - Retourne les coordonnées de la fenêtre et du bouton"""
    from inventory import MAX_INVENTORY_SIZE

    # Dimensions de la fenêtre d'inventaire
    inv_width = 400
    inv_height = 500
    inv_x = (SCREEN_WIDTH - inv_width) // 2
    inv_y = (SCREEN_HEIGHT - inv_height) // 2

    # Couleurs
    BG_COLOR = (40, 40, 40)
    BORDER_COLOR = (200, 200, 200)
    TEXT_COLOR = (255, 255, 255)
    TITLE_COLOR = (255, 255, 100)
    BUTTON_COLOR = (180, 50, 50)

    # Fond semi-transparent
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Fond de la fenêtre d'inventaire
    pygame.draw.rect(screen, BG_COLOR, (inv_x, inv_y, inv_width, inv_height))
    pygame.draw.rect(screen, BORDER_COLOR, (inv_x, inv_y, inv_width, inv_height), 3)

    # Police
    title_font = pygame.font.Font(None, 36)
    item_font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 22)
    button_font = pygame.font.Font(None, 24)

    # Titre
    title_text = title_font.render(f"INVENTAIRE ({len(inventory)}/{MAX_INVENTORY_SIZE})", True, TITLE_COLOR)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, inv_y + 30))
    screen.blit(title_text, title_rect)

    # Ligne de séparation
    pygame.draw.line(screen, BORDER_COLOR,
                     (inv_x + 10, inv_y + 60),
                     (inv_x + inv_width - 10, inv_y + 60), 2)

    # Afficher les items
    item_rects = []

    if not inventory:
        empty_text = item_font.render("(vide)", True, (150, 150, 150))
        empty_rect = empty_text.get_rect(center=(SCREEN_WIDTH // 2, inv_y + 100))
        screen.blit(empty_text, empty_rect)
    else:
        y_offset = inv_y + 80
        for i, item in enumerate(inventory):
            is_equipped = item.get("equipped", False)

            if is_equipped:
                bg_color = (50, 100, 50)
                text_color = (200, 255, 200)
                icon = "⚔️ " if item["type"] == "weapon" else "🛡️ " if item["type"] == "armor" else "✓ "
            else:
                bg_color = None
                text_color = TEXT_COLOR
                icon = ""

            item_rect = (inv_x + 15, y_offset - 5, inv_width - 30, 30)
            item_rects.append((item, item_rect))

            if bg_color:
                pygame.draw.rect(screen, bg_color, item_rect)

            item_text = f"{i+1}. {icon}{item['name']}"
            text_surface = item_font.render(item_text, True, text_color)
            screen.blit(text_surface, (inv_x + 20, y_offset))

            type_text = f"({item['type']})"
            type_surface = small_font.render(type_text, True, (180, 180, 180))
            screen.blit(type_surface, (inv_x + 300, y_offset + 5))

            y_offset += 35

            if y_offset > inv_y + inv_height - 100:
                more_text = small_font.render("...", True, (150, 150, 150))
                screen.blit(more_text, (inv_x + 20, y_offset))
                break

    # Bouton "Fermer"
    button_width = 100
    button_height = 35
    button_x = (SCREEN_WIDTH - button_width) // 2
    button_y = inv_y + inv_height - 50

    pygame.draw.rect(screen, BUTTON_COLOR, (button_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, BORDER_COLOR, (button_x, button_y, button_width, button_height), 2)

    button_text = button_font.render("Fermer", True, TEXT_COLOR)
    button_text_rect = button_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    screen.blit(button_text, button_text_rect)

    # Retourner les coordonnées de la fenêtre, du bouton ET des items
    return {
        'window': (inv_x, inv_y, inv_width, inv_height),
        'close_button': (button_x, button_y, button_width, button_height),
        'items': item_rects
    }

def draw_inventory_button(screen, SCREEN_WIDTH, inventory_open):
    """Dessine le bouton pour ouvrir/fermer l'inventaire"""

    button_width = 60
    button_height = 40
    button_x = SCREEN_WIDTH - button_width - 10
    button_y = 10

    if inventory_open:
        button_color = (100, 200, 100)
    else:
        button_color = (150, 150, 150)

    border_color = (255, 255, 255)

    pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, border_color, (button_x, button_y, button_width, button_height), 2)

    button_font = pygame.font.Font(None, 32)
    text = button_font.render("I", True, (255, 255, 255))
    text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    screen.blit(text, text_rect)

    return (button_x, button_y, button_width, button_height)


# ==========================================
# TOOLTIPS (positions écran, pas de caméra)
# ==========================================

def draw_tooltip(screen, item, mouse_x, mouse_y, SCREEN_WIDTH, SCREEN_HEIGHT):
    """Dessine une infobulle avec les stats de l'item au survol"""

    tooltip_width = 200
    tooltip_padding = 10
    line_height = 25

    lines = []
    lines.append(item['name'])
    lines.append(f"Type: {item['type']}")

    if item['type'] == 'weapon':
        lines.append(f"+{item.get('attack', 0)} Attaque")
    elif item['type'] == 'armor':
        lines.append(f"+{item.get('defense', 0)} Défense")
    elif item['type'] == 'food':
        lines.append(f"+{item.get('hunger_restore', 0)} Faim")

    if item.get('equipped', False):
        lines.append("✓ Équipé")

    tooltip_height = len(lines) * line_height + tooltip_padding * 2

    tooltip_x = mouse_x + 15
    tooltip_y = mouse_y - tooltip_height // 2

    if tooltip_x + tooltip_width > SCREEN_WIDTH:
        tooltip_x = mouse_x - tooltip_width - 15
    if tooltip_y < 0:
        tooltip_y = 0
    elif tooltip_y + tooltip_height > SCREEN_HEIGHT:
        tooltip_y = SCREEN_HEIGHT - tooltip_height

    BG_COLOR = (30, 30, 30)
    BORDER_COLOR = (200, 200, 100)
    TEXT_COLOR = (255, 255, 255)
    TITLE_COLOR = (255, 255, 100)

    pygame.draw.rect(screen, BG_COLOR, (tooltip_x, tooltip_y, tooltip_width, tooltip_height))
    pygame.draw.rect(screen, BORDER_COLOR, (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2)

    tooltip_font = pygame.font.Font(None, 22)
    y_offset = tooltip_y + tooltip_padding

    for i, line in enumerate(lines):
        if i == 0:
            font = pygame.font.Font(None, 26)
            color = TITLE_COLOR
        else:
            font = tooltip_font
            color = TEXT_COLOR

        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (tooltip_x + tooltip_padding, y_offset))
        y_offset += line_height

def draw_enemy_tooltip(screen, enemy, mouse_x, mouse_y, SCREEN_WIDTH, SCREEN_HEIGHT):
    """Dessine une infobulle avec les stats de l'ennemi au survol"""

    tooltip_width = 240
    tooltip_padding = 10
    line_height = 25

    lines = []
    lines.append(enemy.get("name", "Ennemi"))
    lines.append(f"PV: {enemy['hp']}/{enemy['max_hp']}")
    lines.append(f"ATK: {enemy['attack']}  DEF: {enemy.get('defense', 0)}")

    tooltip_height = len(lines) * line_height + tooltip_padding * 2

    tooltip_x = mouse_x + 15
    tooltip_y = mouse_y - tooltip_height // 2

    if tooltip_x + tooltip_width > SCREEN_WIDTH:
        tooltip_x = mouse_x - tooltip_width - 15
    if tooltip_y < 0:
        tooltip_y = 0
    elif tooltip_y + tooltip_height > SCREEN_HEIGHT:
        tooltip_y = SCREEN_HEIGHT - tooltip_height

    BG_COLOR = (40, 20, 20)
    BORDER_COLOR = (200, 100, 100)
    TEXT_COLOR = (255, 255, 255)
    TITLE_COLOR = (255, 150, 150)
    HP_COLOR = (255, 100, 100)

    pygame.draw.rect(screen, BG_COLOR, (tooltip_x, tooltip_y, tooltip_width, tooltip_height))
    pygame.draw.rect(screen, BORDER_COLOR, (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2)

    tooltip_font = pygame.font.Font(None, 22)
    y_offset = tooltip_y + tooltip_padding

    for i, line in enumerate(lines):
        if i == 0:
            font = pygame.font.Font(None, 26)
            color = TITLE_COLOR
        elif "PV:" in line:
            font = tooltip_font
            color = HP_COLOR
        else:
            font = tooltip_font
            color = TEXT_COLOR

        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (tooltip_x + tooltip_padding, y_offset))
        y_offset += line_height
