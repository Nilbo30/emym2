"""
Logique de jeu : combat, items, game over, etc.
"""

from player import player, check_hunger


def get_item_at(x, y, items):
    """Trouve un objet à la position (x, y). Retourne l'objet ou None"""
    for item in items:
        if item["x"] == x and item["y"] == y:
            return item
    return None


def pickup_item(item, items):
    """Ramasse un objet et le met dans l'inventaire"""
    from inventory import add_to_inventory, equip_item, get_inventory
    from player import get_valid_slot_for_item

    # Retirer l'objet du sol
    items.remove(item)

    # Ajouter à l'inventaire
    success = add_to_inventory(item)

    if not success:
        # Si inventaire plein, remettre l'objet au sol
        items.append(item)
        print("Impossible de ramasser : inventaire plein !")
        return

    # Auto-équiper si le slot est libre
    item_type = item.get("type")
    if item_type in ["weapon", "armor", "shield", "accessory"]:
        slot = get_valid_slot_for_item(item)
        if slot and player["equipment"].get(slot) is None:
            equip_item(item)
            print(f"  -> Équipé automatiquement [{slot}]")
        else:
            print(f"  -> Ajouté à l'inventaire")


def combat(enemy, enemies):
    """Gère le combat entre le joueur et un ennemi - Retourne True si le joueur meurt"""
    from skills import gain_xp, get_weapon_skill_key, on_hit_armor_xp

    # --- XP de l'arme utilisée ---
    weapon = player["equipment"].get("main_hand")
    if weapon and weapon.get("weapon_type"):
        skill_key = get_weapon_skill_key(weapon["weapon_type"])
        if skill_key:
            gain_xp(skill_key, 1.0)

    # Le joueur attaque l'ennemi
    damage_to_enemy = player["attack"] - enemy.get("defense", 0)
    if damage_to_enemy < 1:
        damage_to_enemy = 1

    enemy["hp"] -= damage_to_enemy
    print(f"Vous infligez {damage_to_enemy} degats ! (HP: {enemy['hp']}/{enemy['max_hp']})")

    # Vérifier si l'ennemi est mort
    if enemy["hp"] <= 0:
        print("L'ennemi est vaincu !")
        enemies.remove(enemy)
        return False

    # L'ennemi riposte
    damage_to_player = enemy["attack"] - player["defense"]
    if damage_to_player < 1:
        damage_to_player = 1

    player["hp"] -= damage_to_player
    print(f"L'ennemi vous inflige {damage_to_player} degats ! (Vos HP: {player['hp']}/{player['max_hp']})")

    # --- XP bonus armure quand touché ---
    on_hit_armor_xp()

    # Le combat consomme de la faim
    player["hunger"] -= 1

    # Vérifier si le joueur est mort
    if player["hp"] <= 0:
        return True

    if check_hunger():
        return True

    return False


def can_move(x, y, game_map, MAP_WIDTH, MAP_HEIGHT):
    """Vérifie si la case est libre (pas un mur)"""
    if x < 0 or x >= MAP_WIDTH or y < 0 or y >= MAP_HEIGHT:
        return False
    return game_map[y][x] != '#'


def toggle_equip_item(item):
    """
    Équipe ou déséquipe un item selon son état actuel.
    Retourne True si l'action a réussi.
    """
    from inventory import equip_item, unequip_item, is_equipped

    item_type = item.get("type")

    # Seulement pour équipables
    if item_type not in ["weapon", "armor", "shield", "accessory"]:
        return False

    if is_equipped(item):
        unequip_item(item)
        return True
    else:
        equip_item(item)
        return True


def consume_item(item):
    """
    Consomme un item (nourriture).
    Retourne True si l'item doit être retiré de l'inventaire.
    """
    from inventory import remove_from_inventory

    if item["type"] == "food":
        player["hunger"] += item.get("hunger_restore", 0)
        if player["hunger"] > player["max_hunger"]:
            player["hunger"] = player["max_hunger"]
        print(f"Vous mangez : {item['name']} (+{item['hunger_restore']} Faim)")
        print(f"Faim : {player['hunger']}/{player['max_hunger']}")
        remove_from_inventory(item)
        return True

    return False
