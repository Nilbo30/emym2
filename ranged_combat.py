"""
Système de combat à distance (Arc, Arbalète).
Algorithme de Bresenham pour la ligne de vue et la trajectoire.
"""

from player import player, check_hunger

# Types d'armes qui peuvent tirer à distance
RANGED_WEAPON_TYPES = {"Arc", "Arbalète"}


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
        if (cx, cy) != (x0, y0):
            points.append((cx, cy))

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
        if lx == target_x and ly == target_y:
            return True
        if game_map[ly][lx] == '#':
            return False

    return True


def player_has_ranged_weapon():
    """Vérifie si le joueur a une arme à distance équipée en main_hand"""
    weapon = player["equipment"].get("main_hand")
    if weapon is None:
        return False
    return weapon.get("weapon_type") in RANGED_WEAPON_TYPES


# Alias pour compatibilité
player_has_bow = player_has_ranged_weapon


def ranged_attack(enemy, enemies, game_map):
    """
    Effectue une attaque à distance sur un ennemi.
    Vérifie la ligne de vue avant de tirer.
    Retourne : (success, player_died)
    """
    from skills import gain_xp, get_weapon_skill_key

    px, py = player["x"], player["y"]
    ex, ey = enemy["x"], enemy["y"]

    # Vérifier la ligne de vue
    if not has_line_of_sight(px, py, ex, ey, game_map):
        print("Ligne de vue bloquee par un mur !")
        return False, False

    # XP de l'arme à distance
    weapon = player["equipment"].get("main_hand")
    weapon_type = weapon.get("weapon_type", "") if weapon else ""
    weapon_name = weapon.get("name", "Arc") if weapon else "Arc"
    skill_key = get_weapon_skill_key(weapon_type)
    if skill_key:
        gain_xp(skill_key, 1.0)

    # Calculer les dégâts
    damage = player["attack"] - enemy.get("defense", 0)
    if damage < 1:
        damage = 1

    enemy["hp"] -= damage
    print(f"[Tir] Vous tirez sur {enemy.get('name', 'ennemi')} avec {weapon_name} !")
    print(f"  -> {damage} degats ! (HP: {enemy['hp']}/{enemy['max_hp']})")

    # Ennemi mort ?
    if enemy["hp"] <= 0:
        print(f"  -> {enemy.get('name', 'ennemi')} est vaincu !")
        enemies.remove(enemy)

    # Tirer consomme 1 de faim
    player["hunger"] -= 1
    player_died = check_hunger()

    return True, player_died
