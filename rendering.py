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

visible_tiles = set()
camera_x = 0
camera_y = 0

# Noms lisibles des slots
SLOT_NAMES = {
    "main_hand": "Main",
    "off_hand": "Second.",
    "body": "Torse",
    "head": "Tête",
    "hands": "Mains",
    "feet": "Pieds",
    "ring1": "Anneau 1",
    "ring2": "Anneau 2",
    "amulet": "Amulette",
}


# ==========================================
# CAMÉRA
# ==========================================

def update_camera(player_x, player_y, map_width, map_height):
    """Centre la caméra sur le joueur."""
    global camera_x, camera_y
    camera_x = player_x - VIEWPORT_WIDTH // 2
    camera_y = player_y - VIEWPORT_HEIGHT // 2
    camera_x = max(0, min(camera_x, map_width - VIEWPORT_WIDTH))
    camera_y = max(0, min(camera_y, map_height - VIEWPORT_HEIGHT))


def get_camera():
    return camera_x, camera_y


def set_visible_tiles(tiles):
    global visible_tiles
    visible_tiles = set(tiles)


# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================

def _world_to_screen(world_x, world_y, tile_size):
    return (world_x - camera_x) * tile_size, (world_y - camera_y) * tile_size


def _is_on_screen(world_x, world_y):
    vx = world_x - camera_x
    vy = world_y - camera_y
    return 0 <= vx < VIEWPORT_WIDTH and 0 <= vy < VIEWPORT_HEIGHT


# ==========================================
# DESSIN DE LA CARTE
# ==========================================

def draw_map(screen, game_map, explored, font, TILE_SIZE, MAP_HEIGHT, MAP_WIDTH):
    """Dessine la portion visible de la carte avec fog of war."""
    for vy in range(VIEWPORT_HEIGHT):
        for vx in range(VIEWPORT_WIDTH):
            wx = camera_x + vx
            wy = camera_y + vy

            if wx < 0 or wx >= MAP_WIDTH or wy < 0 or wy >= MAP_HEIGHT:
                continue

            tile = game_map[wy][wx]
            is_visible = (wx, wy) in visible_tiles
            is_explored = explored[wy][wx]

            if not is_explored:
                continue

            sx = vx * TILE_SIZE
            sy = vy * TILE_SIZE

            if is_visible:
                if tile == '#':
                    color = (128, 128, 128)
                elif tile == '.':
                    color = (30, 30, 35)
                elif tile == '>':
                    color = (255, 255, 0)
                else:
                    color = (255, 255, 255)
            else:
                if tile == '#':
                    color = (50, 50, 55)
                elif tile == '.':
                    color = (18, 18, 22)
                elif tile == '>':
                    color = (80, 80, 0)
                else:
                    color = (40, 40, 40)

            if tile == '.' or tile == '>':
                pygame.draw.rect(screen, color, (sx, sy, TILE_SIZE, TILE_SIZE))

            if tile != '.':
                text = font.render(tile, True, color)
                text_rect = text.get_rect(center=(sx + TILE_SIZE // 2,
                                                   sy + TILE_SIZE // 2))
                screen.blit(text, text_rect)


# ==========================================
# DESSIN DES ENTITÉS
# ==========================================

def draw_player(screen, player, font, TILE_SIZE):
    if not _is_on_screen(player["x"], player["y"]):
        return
    sx, sy = _world_to_screen(player["x"], player["y"], TILE_SIZE)
    text = font.render('@', True, (0, 255, 0))
    text_rect = text.get_rect(center=(sx + TILE_SIZE // 2, sy + TILE_SIZE // 2))
    screen.blit(text, text_rect)


def draw_enemies(screen, enemies, font, TILE_SIZE):
    for enemy in enemies:
        if (enemy["x"], enemy["y"]) not in visible_tiles:
            continue
        if not _is_on_screen(enemy["x"], enemy["y"]):
            continue
        sx, sy = _world_to_screen(enemy["x"], enemy["y"], TILE_SIZE)
        text = font.render(enemy["symbol"], True, enemy["color"])
        text_rect = text.get_rect(center=(sx + TILE_SIZE // 2, sy + TILE_SIZE // 2))
        screen.blit(text, text_rect)


def draw_items(screen, items, font, TILE_SIZE):
    for item in items:
        if (item["x"], item["y"]) not in visible_tiles:
            continue
        if not _is_on_screen(item["x"], item["y"]):
            continue
        sx, sy = _world_to_screen(item["x"], item["y"], TILE_SIZE)
        text = font.render(item["symbol"], True, item["color"])
        text_rect = text.get_rect(center=(sx + TILE_SIZE // 2, sy + TILE_SIZE // 2))
        screen.blit(text, text_rect)


# ==========================================
# INTERFACE UTILISATEUR
# ==========================================

def draw_ui(screen, player, current_floor, SCREEN_WIDTH):
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)

    ui_font = pygame.font.Font(None, 24)

    hp_text = ui_font.render(f"PV: {player['hp']}/{player['max_hp']}", True, WHITE)
    screen.blit(hp_text, (10, 10))

    mana_text = ui_font.render(f"Mana: {player['mana']}/{player['max_mana']}", True, WHITE)
    screen.blit(mana_text, (10, 35))

    floor_text = ui_font.render(f"Etage: {current_floor}", True, YELLOW)
    screen.blit(floor_text, (SCREEN_WIDTH - 120, 10))

    stats_text = ui_font.render(f"ATK: {player['attack']}  DEF: {player['defense']}", True, WHITE)
    screen.blit(stats_text, (10, 60))

    if player['hunger'] > 50:
        hunger_color = GREEN
    elif player['hunger'] > 20:
        hunger_color = YELLOW
    else:
        hunger_color = (255, 0, 0)

    hunger_text = ui_font.render(f"Faim: {player['hunger']}/{player['max_hunger']}", True, hunger_color)
    screen.blit(hunger_text, (10, 85))


# ==========================================
# INVENTAIRE (popup avec onglets sac/équipement)
# ==========================================

def draw_inventory(screen, inventory, SCREEN_WIDTH, SCREEN_HEIGHT, active_tab="bag"):
    """
    Dessine l'inventaire avec deux onglets : Sac et Équipement.
    Retourne les coordonnées cliquables.
    """
    from inventory import MAX_INVENTORY_SIZE
    from player import player, EQUIPMENT_SLOTS

    # Dimensions
    inv_width = 450
    inv_height = 520
    inv_x = (SCREEN_WIDTH - inv_width) // 2
    inv_y = (SCREEN_HEIGHT - inv_height) // 2

    # Couleurs
    BG_COLOR = (40, 40, 40)
    BORDER_COLOR = (200, 200, 200)
    TEXT_COLOR = (255, 255, 255)
    TITLE_COLOR = (255, 255, 100)
    BUTTON_COLOR = (180, 50, 50)
    TAB_ACTIVE = (80, 80, 120)
    TAB_INACTIVE = (50, 50, 60)
    EQUIPPED_BG = (50, 100, 50)
    SLOT_EMPTY = (60, 60, 70)

    # Overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Fond
    pygame.draw.rect(screen, BG_COLOR, (inv_x, inv_y, inv_width, inv_height))
    pygame.draw.rect(screen, BORDER_COLOR, (inv_x, inv_y, inv_width, inv_height), 3)

    # Polices
    title_font = pygame.font.Font(None, 36)
    item_font = pygame.font.Font(None, 26)
    small_font = pygame.font.Font(None, 22)
    button_font = pygame.font.Font(None, 24)
    tag_font = pygame.font.Font(None, 20)

    # Onglets
    tab_width = inv_width // 2
    tab_height = 35
    tab_y = inv_y

    tab_bag_rect = (inv_x, tab_y, tab_width, tab_height)
    tab_equip_rect = (inv_x + tab_width, tab_y, tab_width, tab_height)

    # Dessiner les onglets
    pygame.draw.rect(screen, TAB_ACTIVE if active_tab == "bag" else TAB_INACTIVE, tab_bag_rect)
    pygame.draw.rect(screen, TAB_ACTIVE if active_tab == "equip" else TAB_INACTIVE, tab_equip_rect)
    pygame.draw.rect(screen, BORDER_COLOR, tab_bag_rect, 2)
    pygame.draw.rect(screen, BORDER_COLOR, tab_equip_rect, 2)

    bag_text = button_font.render(f"Sac ({len(inventory)}/{MAX_INVENTORY_SIZE})", True, TEXT_COLOR)
    bag_text_rect = bag_text.get_rect(center=(inv_x + tab_width // 2, tab_y + tab_height // 2))
    screen.blit(bag_text, bag_text_rect)

    equip_text = button_font.render("Equipement", True, TEXT_COLOR)
    equip_text_rect = equip_text.get_rect(center=(inv_x + tab_width + tab_width // 2, tab_y + tab_height // 2))
    screen.blit(equip_text, equip_text_rect)

    # Contenu selon l'onglet actif
    content_y = tab_y + tab_height + 10
    item_rects = []

    if active_tab == "bag":
        # --- ONGLET SAC ---
        if not inventory:
            empty_text = item_font.render("(vide)", True, (150, 150, 150))
            empty_rect = empty_text.get_rect(center=(SCREEN_WIDTH // 2, content_y + 40))
            screen.blit(empty_text, empty_rect)
        else:
            y_offset = content_y
            for i, item in enumerate(inventory):
                is_equipped = item.get("equipped", False)
                item_type = item.get("type", "")

                # Fond coloré si équipé
                if is_equipped:
                    bg_color = EQUIPPED_BG
                    text_color = (200, 255, 200)
                else:
                    bg_color = None
                    text_color = TEXT_COLOR

                item_rect = (inv_x + 10, y_offset - 2, inv_width - 20, 28)
                item_rects.append((item, item_rect))

                if bg_color:
                    pygame.draw.rect(screen, bg_color, item_rect)

                # Symbole coloré
                sym_surface = item_font.render(item.get("symbol", "?"), True, item.get("color", TEXT_COLOR))
                screen.blit(sym_surface, (inv_x + 15, y_offset))

                # Nom
                name = item.get("name", "???")
                if len(name) > 28:
                    name = name[:26] + ".."
                name_surface = item_font.render(name, True, text_color)
                screen.blit(name_surface, (inv_x + 35, y_offset))

                # Slot info si équipé
                if is_equipped:
                    slot_name = SLOT_NAMES.get(item.get("equipped_slot", ""), "")
                    slot_surface = tag_font.render(f"[{slot_name}]", True, (150, 255, 150))
                    screen.blit(slot_surface, (inv_x + inv_width - 80, y_offset + 2))

                # Stats courtes à droite
                stat_text = ""
                if item_type == "weapon":
                    atk = item.get("attack", 0) + item.get("elemental_attack", 0)
                    stat_text = f"+{atk} ATK"
                elif item_type in ["armor", "shield"]:
                    stat_text = f"+{item.get('defense', 0)} DEF"
                elif item_type == "food":
                    stat_text = f"+{item.get('hunger_restore', 0)} Faim"
                elif item_type == "accessory":
                    bonuses = item.get("bonuses", {})
                    parts = [f"+{v} {k}" for k, v in bonuses.items()]
                    stat_text = ", ".join(parts) if parts else ""

                if stat_text:
                    stat_surface = tag_font.render(stat_text, True, (180, 180, 180))
                    screen.blit(stat_surface, (inv_x + 300, y_offset + 4))

                y_offset += 30

                if y_offset > inv_y + inv_height - 70:
                    more_text = small_font.render("...", True, (150, 150, 150))
                    screen.blit(more_text, (inv_x + 15, y_offset))
                    break

    else:
        # --- ONGLET ÉQUIPEMENT ---
        y_offset = content_y
        for slot in EQUIPMENT_SLOTS:
            item = player["equipment"].get(slot)
            slot_label = SLOT_NAMES.get(slot, slot)

            slot_rect = (inv_x + 10, y_offset - 2, inv_width - 20, 28)

            if item:
                item_rects.append((item, slot_rect))
                pygame.draw.rect(screen, EQUIPPED_BG, slot_rect)

                # Label du slot
                label_surface = small_font.render(f"{slot_label}:", True, (150, 200, 150))
                screen.blit(label_surface, (inv_x + 15, y_offset + 2))

                # Symbole + nom
                sym_surface = item_font.render(item.get("symbol", "?"), True, item.get("color", TEXT_COLOR))
                screen.blit(sym_surface, (inv_x + 90, y_offset))

                name = item.get("name", "???")
                if len(name) > 22:
                    name = name[:20] + ".."
                name_surface = item_font.render(name, True, (200, 255, 200))
                screen.blit(name_surface, (inv_x + 110, y_offset))

                # Stats
                stat_text = ""
                if item.get("type") == "weapon":
                    atk = item.get("attack", 0) + item.get("elemental_attack", 0)
                    stat_text = f"+{atk} ATK"
                elif item.get("type") in ["armor", "shield"]:
                    stat_text = f"+{item.get('defense', 0)} DEF"
                elif item.get("type") == "accessory":
                    bonuses = item.get("bonuses", {})
                    parts = [f"+{v} {k}" for k, v in bonuses.items()]
                    stat_text = ", ".join(parts) if parts else ""

                if stat_text:
                    stat_surface = tag_font.render(stat_text, True, (180, 180, 180))
                    screen.blit(stat_surface, (inv_x + inv_width - 100, y_offset + 4))
            else:
                # Slot vide
                pygame.draw.rect(screen, SLOT_EMPTY, slot_rect)
                label_surface = small_font.render(f"{slot_label}:", True, (120, 120, 130))
                screen.blit(label_surface, (inv_x + 15, y_offset + 2))
                empty_surface = small_font.render("(vide)", True, (90, 90, 100))
                screen.blit(empty_surface, (inv_x + 110, y_offset + 2))

            y_offset += 32

    # Ligne de séparation avant le bouton
    sep_y = inv_y + inv_height - 55
    pygame.draw.line(screen, BORDER_COLOR, (inv_x + 10, sep_y), (inv_x + inv_width - 10, sep_y), 1)

    # Bouton "Fermer"
    button_width = 100
    button_height = 35
    button_x = (SCREEN_WIDTH - button_width) // 2
    button_y = inv_y + inv_height - 48

    pygame.draw.rect(screen, BUTTON_COLOR, (button_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, BORDER_COLOR, (button_x, button_y, button_width, button_height), 2)

    close_text = button_font.render("Fermer", True, TEXT_COLOR)
    close_rect = close_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    screen.blit(close_text, close_rect)

    return {
        'window': (inv_x, inv_y, inv_width, inv_height),
        'close_button': (button_x, button_y, button_width, button_height),
        'items': item_rects,
        'tab_bag': tab_bag_rect,
        'tab_equip': tab_equip_rect,
        'active_tab': active_tab,
    }


def draw_inventory_button(screen, SCREEN_WIDTH, inventory_open):
    button_width = 60
    button_height = 40
    button_x = SCREEN_WIDTH - button_width - 10
    button_y = 10

    if inventory_open:
        button_color = (100, 200, 100)
    else:
        button_color = (150, 150, 150)

    pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, (255, 255, 255), (button_x, button_y, button_width, button_height), 2)

    button_font = pygame.font.Font(None, 32)
    text = button_font.render("I", True, (255, 255, 255))
    text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    screen.blit(text, text_rect)

    return (button_x, button_y, button_width, button_height)


# ==========================================
# TOOLTIPS
# ==========================================

def draw_tooltip(screen, item, mouse_x, mouse_y, SCREEN_WIDTH, SCREEN_HEIGHT):
    """Dessine une infobulle enrichie avec tags, élément et stats détaillées"""

    tooltip_width = 240
    tooltip_padding = 10
    line_height = 22

    lines = []
    line_colors = []

    # Nom de l'item
    lines.append(item.get('name', '???'))
    line_colors.append(item.get('color', (255, 255, 100)))

    # Tags
    tags = item.get('tags', [])
    if tags:
        lines.append("Tags: " + ", ".join(tags))
        line_colors.append((180, 180, 180))

    # Type / Slot
    item_type = item.get('type', '')
    slot = item.get('equipped_slot') or item.get('slot', '')
    slot_label = SLOT_NAMES.get(slot, slot) if slot else ""
    if item_type and slot_label:
        lines.append(f"Type: {item_type} | Slot: {slot_label}")
        line_colors.append((150, 150, 200))

    # Stats
    if item_type == 'weapon':
        lines.append(f"+{item.get('attack', 0)} Attaque")
        line_colors.append((255, 200, 150))
        elem_atk = item.get('elemental_attack', 0)
        if elem_atk > 0:
            element = item.get('element', '?')
            lines.append(f"+{elem_atk} {element}")
            line_colors.append(item.get('color', (200, 200, 200)))
        if item.get('two_handed'):
            lines.append("(Deux mains)")
            line_colors.append((200, 150, 100))

    elif item_type in ['armor', 'shield']:
        lines.append(f"+{item.get('defense', 0)} Defense")
        line_colors.append((150, 200, 255))

    elif item_type == 'food':
        lines.append(f"+{item.get('hunger_restore', 0)} Faim")
        line_colors.append((255, 200, 100))

    elif item_type == 'accessory':
        for stat, value in item.get('bonuses', {}).items():
            lines.append(f"+{value} {stat}")
            line_colors.append((200, 200, 255))

    # Statut équipé
    if item.get('equipped', False):
        lines.append(">> Equipe <<")
        line_colors.append((100, 255, 100))

    tooltip_height = len(lines) * line_height + tooltip_padding * 2

    tooltip_x = mouse_x + 15
    tooltip_y = mouse_y - tooltip_height // 2

    if tooltip_x + tooltip_width > SCREEN_WIDTH:
        tooltip_x = mouse_x - tooltip_width - 15
    if tooltip_y < 0:
        tooltip_y = 0
    elif tooltip_y + tooltip_height > SCREEN_HEIGHT:
        tooltip_y = SCREEN_HEIGHT - tooltip_height

    pygame.draw.rect(screen, (30, 30, 30), (tooltip_x, tooltip_y, tooltip_width, tooltip_height))
    pygame.draw.rect(screen, (200, 200, 100), (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2)

    y_offset = tooltip_y + tooltip_padding
    for i, line in enumerate(lines):
        if i == 0:
            font = pygame.font.Font(None, 26)
        else:
            font = pygame.font.Font(None, 22)
        color = line_colors[i] if i < len(line_colors) else (255, 255, 255)
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (tooltip_x + tooltip_padding, y_offset))
        y_offset += line_height


def draw_enemy_tooltip(screen, enemy, mouse_x, mouse_y, SCREEN_WIDTH, SCREEN_HEIGHT):
    """Dessine une infobulle avec les stats de l'ennemi"""

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
