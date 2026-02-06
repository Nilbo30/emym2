"""
Fonctions d'affichage / rendu graphique
"""

import pygame

# On aura besoin de ces variables globales
visible_tiles = []

def draw_map(screen, game_map, explored, font, TILE_SIZE, MAP_HEIGHT, MAP_WIDTH):
    """Dessine toute la carte avec fog of war"""
    # Couleurs (locales à cette fonction)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile = game_map[y][x]

            # Vérifier si la case est visible ou explorée
            is_visible = (x, y) in visible_tiles
            is_explored = explored[y][x]

            if not is_explored:
                # Case jamais vue = noir total
                continue

            # Choisir la couleur selon le type de case
            if tile == '#':
                color = GRAY
            elif tile == '.':
                color = BLACK
            elif tile == '>':
                color = YELLOW
            else:
                color = WHITE

            # Si pas visible actuellement, assombrir
            if not is_visible:
                color = tuple(c // 3 for c in color)  # 3x plus sombre

            # Dessiner le fond
            if tile == '.':
                pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

            # Dessiner le caractère
            if tile != '.':
                text = font.render(tile, True, color)
                text_rect = text.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2,
                                                   y * TILE_SIZE + TILE_SIZE // 2))
                screen.blit(text, text_rect)


def draw_player(screen, player, font, TILE_SIZE):
    """Dessine le joueur (@)"""
    GREEN = (0, 255, 0)
    text = font.render('@', True, GREEN)
    text_rect = text.get_rect(center=(player["x"] * TILE_SIZE + TILE_SIZE // 2,
                                      player["y"] * TILE_SIZE + TILE_SIZE // 2))
    screen.blit(text, text_rect)


def draw_enemies(screen, enemies, font, TILE_SIZE):
    """Dessine tous les ennemis (seulement ceux visibles)"""
    for enemy in enemies:
        # Ne dessiner que si visible
        if (enemy["x"], enemy["y"]) in visible_tiles:
            text = font.render(enemy["symbol"], True, enemy["color"])
            text_rect = text.get_rect(center=(enemy["x"] * TILE_SIZE + TILE_SIZE // 2,
                                              enemy["y"] * TILE_SIZE + TILE_SIZE // 2))
            screen.blit(text, text_rect)


def draw_items(screen, items, font, TILE_SIZE):
    """Dessine tous les objets au sol (seulement ceux visibles)"""
    for item in items:
        # Ne dessiner que si visible
        if (item["x"], item["y"]) in visible_tiles:
            text = font.render(item["symbol"], True, item["color"])
            text_rect = text.get_rect(center=(item["x"] * TILE_SIZE + TILE_SIZE // 2,
                                              item["y"] * TILE_SIZE + TILE_SIZE // 2))
            screen.blit(text, text_rect)


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
    # Couleur change selon le niveau
    if player['hunger'] > 50:
        hunger_color = GREEN
    elif player['hunger'] > 20:
        hunger_color = YELLOW
    else:
        hunger_color = (255, 0, 0)  # Rouge si très faible

    hunger_text = ui_font.render(f"Faim: {player['hunger']}/{player['max_hunger']}", True, hunger_color)
    screen.blit(hunger_text, (10, 85))


def set_visible_tiles(tiles):
    """Met à jour la liste des cases visibles (appelé depuis main)"""
    global visible_tiles
    visible_tiles = tiles

def draw_inventory(screen, inventory, SCREEN_WIDTH, SCREEN_HEIGHT):
    """Dessine l'inventaire par-dessus le jeu - Retourne les coordonnées de la fenêtre et du bouton"""
    from inventory import MAX_INVENTORY_SIZE

    # Dimensions de la fenêtre d'inventaire
    inv_width = 400
    inv_height = 500
    inv_x = (SCREEN_WIDTH - inv_width) // 2  # Centré horizontalement
    inv_y = (SCREEN_HEIGHT - inv_height) // 2  # Centré verticalement

    # Couleurs
    BG_COLOR = (40, 40, 40)  # Gris foncé
    BORDER_COLOR = (200, 200, 200)  # Gris clair
    TEXT_COLOR = (255, 255, 255)  # Blanc
    TITLE_COLOR = (255, 255, 100)  # Jaune
    BUTTON_COLOR = (180, 50, 50)  # Rouge pour le bouton fermer
    BUTTON_HOVER = (220, 80, 80)  # Rouge plus clair au survol

    # Fond semi-transparent (assombrir le jeu derrière)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)  # Transparence
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Fond de la fenêtre d'inventaire
    pygame.draw.rect(screen, BG_COLOR, (inv_x, inv_y, inv_width, inv_height))
    pygame.draw.rect(screen, BORDER_COLOR, (inv_x, inv_y, inv_width, inv_height), 3)  # Bordure

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
        # Inventaire vide
        empty_text = item_font.render("(vide)", True, (150, 150, 150))
        empty_rect = empty_text.get_rect(center=(SCREEN_WIDTH // 2, inv_y + 100))
        screen.blit(empty_text, empty_rect)
    else:
        # Afficher chaque item
        y_offset = inv_y + 80
        for i, item in enumerate(inventory):
            # Vérifier si l'item est équipé
            is_equipped = item.get("equipped", False)

            # Couleurs selon l'état
            if is_equipped:
                bg_color = (50, 100, 50)  # Fond vert foncé
                text_color = (200, 255, 200)  # Texte vert clair
                icon = "⚔️ " if item["type"] == "weapon" else "🛡️ " if item["type"] == "armor" else "✓ "
            else:
                bg_color = None  # Pas de fond
                text_color = TEXT_COLOR  # Blanc normal
                icon = ""

            # Zone cliquable de l'item
            item_rect = (inv_x + 15, y_offset - 5, inv_width - 30, 30)  # ← AJOUTE
            item_rects.append((item, item_rect))  # ← AJOUTE (tuple: item + sa zone)

            # Dessiner le fond si équipé
            if bg_color:
                pygame.draw.rect(screen, bg_color, item_rect)  # ← MODIFIE (utilise item_rect)

            # Numéro + Icône + Nom
            item_text = f"{i+1}. {icon}{item['name']}"
            text_surface = item_font.render(item_text, True, text_color)
            screen.blit(text_surface, (inv_x + 20, y_offset))

            # Type (arme, armure, nourriture)
            type_text = f"({item['type']})"
            type_surface = small_font.render(type_text, True, (180, 180, 180))
            screen.blit(type_surface, (inv_x + 300, y_offset + 5))

            y_offset += 35  # Espacement entre items

            # Limiter l'affichage si trop d'items (scroll plus tard)
            if y_offset > inv_y + inv_height - 100:
                more_text = small_font.render("...", True, (150, 150, 150))
                screen.blit(more_text, (inv_x + 20, y_offset))
                break

    # Bouton "Fermer" en bas
    button_width = 100
    button_height = 35
    button_x = (SCREEN_WIDTH - button_width) // 2  # Centré
    button_y = inv_y + inv_height - 50

    # Dessiner le bouton
    pygame.draw.rect(screen, BUTTON_COLOR, (button_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, BORDER_COLOR, (button_x, button_y, button_width, button_height), 2)

    # Texte du bouton
    button_text = button_font.render("Fermer", True, TEXT_COLOR)
    button_text_rect = button_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    screen.blit(button_text, button_text_rect)

    # Retourner les coordonnées de la fenêtre, du bouton ET des items
    return {
        'window': (inv_x, inv_y, inv_width, inv_height),
        'close_button': (button_x, button_y, button_width, button_height),
        'items': item_rects  # ← AJOUTE CETTE LIGNE
    }

def draw_inventory_button(screen, SCREEN_WIDTH, inventory_open):
    """Dessine le bouton pour ouvrir/fermer l'inventaire"""

    # Position et taille du bouton (en haut à droite)
    button_width = 60
    button_height = 40
    button_x = SCREEN_WIDTH - button_width - 10  # 10 pixels du bord droit
    button_y = 10  # 10 pixels du haut

    # Couleurs
    if inventory_open:
        button_color = (100, 200, 100)  # Vert si ouvert
    else:
        button_color = (150, 150, 150)  # Gris si fermé

    border_color = (255, 255, 255)  # Blanc

    # Dessiner le bouton
    pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, border_color, (button_x, button_y, button_width, button_height), 2)  # Bordure

    # Texte sur le bouton
    button_font = pygame.font.Font(None, 32)
    text = button_font.render("I", True, (255, 255, 255))
    text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    screen.blit(text, text_rect)

    # Retourner les coordonnées du bouton (pour détecter le clic)
    return (button_x, button_y, button_width, button_height)

def draw_tooltip(screen, item, mouse_x, mouse_y, SCREEN_WIDTH, SCREEN_HEIGHT):
    """Dessine une infobulle avec les stats de l'item au survol"""

    # Dimensions du tooltip
    tooltip_width = 200
    tooltip_padding = 10
    line_height = 25

    # Préparer le texte
    lines = []
    lines.append(item['name'])
    lines.append(f"Type: {item['type']}")

    # Ajouter les stats selon le type
    if item['type'] == 'weapon':
        lines.append(f"+{item.get('attack', 0)} Attaque")
    elif item['type'] == 'armor':
        lines.append(f"+{item.get('defense', 0)} Défense")
    elif item['type'] == 'food':
        lines.append(f"+{item.get('hunger_restore', 0)} Faim")

    # Ajouter statut équipé
    if item.get('equipped', False):
        lines.append("✓ Équipé")

    # Calculer hauteur du tooltip
    tooltip_height = len(lines) * line_height + tooltip_padding * 2

    # Position du tooltip (à côté de la souris, mais reste dans l'écran)
    tooltip_x = mouse_x + 15  # 15px à droite de la souris
    tooltip_y = mouse_y - tooltip_height // 2  # Centré verticalement sur la souris

    # S'assurer que le tooltip reste dans l'écran
    if tooltip_x + tooltip_width > SCREEN_WIDTH:
        tooltip_x = mouse_x - tooltip_width - 15  # À gauche de la souris

    if tooltip_y < 0:
        tooltip_y = 0
    elif tooltip_y + tooltip_height > SCREEN_HEIGHT:
        tooltip_y = SCREEN_HEIGHT - tooltip_height

    # Couleurs
    BG_COLOR = (30, 30, 30)  # Noir foncé
    BORDER_COLOR = (200, 200, 100)  # Jaune doré
    TEXT_COLOR = (255, 255, 255)  # Blanc
    TITLE_COLOR = (255, 255, 100)  # Jaune

    # Dessiner le fond
    pygame.draw.rect(screen, BG_COLOR, (tooltip_x, tooltip_y, tooltip_width, tooltip_height))
    pygame.draw.rect(screen, BORDER_COLOR, (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2)

    # Dessiner le texte
    tooltip_font = pygame.font.Font(None, 22)
    y_offset = tooltip_y + tooltip_padding

    for i, line in enumerate(lines):
        # Première ligne (nom) en jaune et plus gros
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

    # Dimensions du tooltip
    tooltip_width = 180
    tooltip_padding = 10
    line_height = 25

    # Préparer le texte
    lines = []
    lines.append("Ennemi")
    lines.append(f"PV: {enemy['hp']}/{enemy['max_hp']}")
    lines.append(f"ATK: {enemy['attack']}")

    # Calculer hauteur du tooltip
    tooltip_height = len(lines) * line_height + tooltip_padding * 2

    # Position du tooltip (à côté de la souris, mais reste dans l'écran)
    tooltip_x = mouse_x + 15  # 15px à droite de la souris
    tooltip_y = mouse_y - tooltip_height // 2  # Centré verticalement sur la souris

    # S'assurer que le tooltip reste dans l'écran (HORIZONTAL)
    if tooltip_x + tooltip_width > SCREEN_WIDTH:
        tooltip_x = mouse_x - tooltip_width - 15  # À gauche de la souris

    # S'assurer que le tooltip reste dans l'écran (VERTICAL)
    if tooltip_y < 0:
        tooltip_y = 0
    elif tooltip_y + tooltip_height > SCREEN_HEIGHT:
        tooltip_y = SCREEN_HEIGHT - tooltip_height

    # Couleurs
    BG_COLOR = (40, 20, 20)  # Rouge foncé
    BORDER_COLOR = (200, 100, 100)  # Rouge
    TEXT_COLOR = (255, 255, 255)  # Blanc
    TITLE_COLOR = (255, 150, 150)  # Rouge clair
    HP_COLOR = (255, 100, 100)  # Rouge pour les PV

    # Dessiner le fond
    pygame.draw.rect(screen, BG_COLOR, (tooltip_x, tooltip_y, tooltip_width, tooltip_height))
    pygame.draw.rect(screen, BORDER_COLOR, (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2)

    # Dessiner le texte
    tooltip_font = pygame.font.Font(None, 22)
    y_offset = tooltip_y + tooltip_padding

    for i, line in enumerate(lines):
        # Première ligne (titre) en rouge clair
        if i == 0:
            font = pygame.font.Font(None, 26)
            color = TITLE_COLOR
        # Ligne des PV en rouge
        elif "PV:" in line:
            font = tooltip_font
            color = HP_COLOR
        else:
            font = tooltip_font
            color = TEXT_COLOR

        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (tooltip_x + tooltip_padding, y_offset))
        y_offset += line_height
