"""
Système de combat à distance (Arc).
Algorithme de Bresenham pour la ligne de vue et la trajectoire.
"""

from player import player, check_hunger


def bresenham_line(x0, y0, x1, y1):
    """
    Algorithme de Bresenham : retourne la liste des cases (x, y)
    sur la ligne entre (x0, y0) et (x1, y1), SANS le point de départ.
    """
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    cx, cy = x0, y0

    while True:
        # Ne pas inclure le point de départ (position du joueur)
        if (cx, cy) != (x0, y0):
            points.append((cx, cy))

        # Arrivé à destination
        if cx == x1 and cy == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            cx += sx
        if e2 < dx:
            err += dx
            cy += sy

    return points


def has_line_of_sight(start_x, start_y, target_x, target_y, game_map):
    """
    Vérifie qu'il n'y a pas de mur entre start et target.
    Retourne True si la ligne de vue est dégagée, False sinon.
    """
    line = bresenham_line(start_x, start_y, target_x, target_y)

    for (lx, ly) in line:
        # Si on atteint la cible, c'est bon
        if lx == target_x and ly == target_y:
            return True
        # Un mur bloque la ligne de vue
        if game_map[ly][lx] == '#':
            return False

    return True


def player_has_bow():
    """Vérifie si le joueur a un Arc équipé en main_hand"""
    weapon = player["equipment"].get("main_hand")
    if weapon is None:
        return False
    return weapon.get("weapon_type") == "Arc"


def ranged_attack(enemy, enemies, game_map):
    """
    Effectue une attaque à distance sur un ennemi.
    Vérifie la ligne de vue avant de tirer.
    Retourne : (success, player_died)
      - success : True si le tir a eu lieu
      - player_died : True si le joueur meurt (riposte impossible à distance, mais faim)
    """
    px, py = player["x"], player["y"]
    ex, ey = enemy["x"], enemy["y"]

    # Vérifier la ligne de vue
    if not has_line_of_sight(px, py, ex, ey, game_map):
        print("Ligne de vue bloquee par un mur !")
        return False, False

    # Calculer les dégâts (attaque du joueur - défense de l'ennemi)
    damage = player["attack"] - enemy.get("defense", 0)
    if damage < 1:
        damage = 1

    enemy["hp"] -= damage
    weapon = player["equipment"].get("main_hand")
    weapon_name = weapon.get("name", "Arc") if weapon else "Arc"
    print(f"[Arc] Vous tirez sur {enemy.get('name', 'ennemi')} avec {weapon_name} !")
    print(f"  -> {damage} degats ! (HP: {enemy['hp']}/{enemy['max_hp']})")

    # Ennemi mort ?
    if enemy["hp"] <= 0:
        print(f"  -> {enemy.get('name', 'ennemi')} est vaincu !")
        enemies.remove(enemy)

    # Tirer consomme 1 de faim (comme un tour)
    player["hunger"] -= 1
    player_died = check_hunger()

    return True, player_died
