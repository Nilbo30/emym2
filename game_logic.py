"""
Logique de jeu : combat, items, game over, etc.
"""

import random
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

    # Retirer l'objet du sol
    items.remove(item)

    # Ajouter à l'inventaire
    success = add_to_inventory(item)

    if not success:
        # Si inventaire plein, remettre l'objet au sol
        items.append(item)
        print("Impossible de ramasser : inventaire plein !")
        return

    # Système hybride : équiper automatiquement si c'est le premier de ce type
    if item["type"] in ["weapon", "armor"]:
        # Vérifier si on a déjà un item équipé de ce type
        inventory = get_inventory()
        has_equipped = False

        for inv_item in inventory:
            # Si on trouve un item du même type déjà équipé
            if inv_item.get("equipped") and inv_item["type"] == item["type"] and inv_item != item:
                has_equipped = True
                break

        # Si aucun item de ce type n'est équipé, équiper celui-ci
        if not has_equipped:
            equip_item(item)
            print(f"→ Équipé automatiquement (premier {item['type']})")
        else:
            print(f"→ Ajouté à l'inventaire (vous avez déjà un {item['type']} équipé)")

def combat(enemy, enemies):
    """Gère le combat entre le joueur et un ennemi - Retourne True si le joueur meurt"""
    # Le joueur attaque l'ennemi
    damage_to_enemy = player["attack"] - enemy.get("defense", 0)
    if damage_to_enemy < 1:
        damage_to_enemy = 1  # Au minimum 1 dégât

    enemy["hp"] -= damage_to_enemy
    print(f"Vous infligez {damage_to_enemy} dégâts à l'ennemi ! (HP: {enemy['hp']}/{enemy['max_hp']})")

    # Vérifier si l'ennemi est mort
    if enemy["hp"] <= 0:
        print("L'ennemi est vaincu !")
        enemies.remove(enemy)  # Retirer l'ennemi de la liste
        return False  # Joueur pas mort

    # L'ennemi riposte
    damage_to_player = enemy["attack"] - player["defense"]
    if damage_to_player < 1:
        damage_to_player = 1  # Au minimum 1 dégât

    player["hp"] -= damage_to_player
    print(f"L'ennemi vous inflige {damage_to_player} dégâts ! (Vos HP: {player['hp']}/{player['max_hp']})")

    # Le combat consomme aussi de la faim
    player["hunger"] -= 1

    # Vérifier si le joueur est mort
    if player["hp"] <= 0:
        return True  # Joueur mort

    # Vérifier la faim
    if check_hunger():
        return True  # Joueur mort de faim

    return False  # Joueur vivant


def spawn_items(num_items, rooms, game_map, MAP_WIDTH, MAP_HEIGHT):
    """Crée des objets aléatoires sur la carte"""
    items = []

    # Types d'objets possibles
    item_types = [
        {"name": "Épée en Fer", "type": "weapon", "attack": 5, "symbol": "s", "color": (200, 200, 200)},
        {"name": "Épée en Argent", "type": "weapon", "attack": 8, "symbol": "s", "color": (220, 220, 255)},
        {"name": "Hache", "type": "weapon", "attack": 7, "symbol": "h", "color": (150, 100, 50)},
        {"name": "Dague", "type": "weapon", "attack": 4, "symbol": "d", "color": (100, 100, 100)},
        {"name": "Armure en Cuir", "type": "armor", "defense": 3, "symbol": "a", "color": (139, 69, 19)},
        {"name": "Armure en Fer", "type": "armor", "defense": 5, "symbol": "a", "color": (150, 150, 150)},
        {"name": "Bouclier", "type": "armor", "defense": 4, "symbol": "b", "color": (100, 100, 200)},
        # NOURRITURE
        {"name": "Ration", "type": "food", "hunger_restore": 30, "symbol": "%", "color": (255, 200, 100)},
        {"name": "Pain", "type": "food", "hunger_restore": 20, "symbol": "%", "color": (210, 180, 140)},
        {"name": "Viande", "type": "food", "hunger_restore": 50, "symbol": "%", "color": (200, 100, 100)},
    ]

    for _ in range(num_items):
        # Trouver une position libre
        attempts = 0
        while attempts < 100:  # Éviter boucle infinie
            x = random.randint(2, MAP_WIDTH - 3)
            y = random.randint(2, MAP_HEIGHT - 3)

            # Vérifier que c'est du sol
            if game_map[y][x] == '.':
                # Vérifier qu'il n'y a pas déjà un objet ici
                if not any(item["x"] == x and item["y"] == y for item in items):
                    # Choisir un type d'objet au hasard
                    item_template = random.choice(item_types)

                    # Créer l'objet
                    item = item_template.copy()
                    item["x"] = x
                    item["y"] = y

                    items.append(item)
                    break

            attempts += 1

    return items


def can_move(x, y, game_map, MAP_WIDTH, MAP_HEIGHT):
    """Vérifie si la case est libre (pas un mur)"""
    if x < 0 or x >= MAP_WIDTH or y < 0 or y >= MAP_HEIGHT:
        return False
    return game_map[y][x] != '#'

def toggle_equip_item(item):
    """
    Équipe ou déséquipe un item selon son état actuel
    Retourne True si l'action a réussi
    """
    from inventory import equip_item, unequip_item, is_equipped

    item_type = item.get("type")

    # Seulement pour armes et armures
    if item_type not in ["weapon", "armor"]:
        return False

    # Si déjà équipé → déséquiper
    if is_equipped(item):
        remove_item_stats(item)  # Retirer les stats
        unequip_item(item)
        return True

    # Sinon → équiper (gère automatiquement le remplacement)
    else:
        equip_item(item)  # Cette fonction gère tout maintenant
        return True
def consume_item(item):
    """
    Consomme un item (nourriture, potion, etc.)
    Retourne True si l'item doit être retiré de l'inventaire
    """
    from inventory import remove_from_inventory

    if item["type"] == "food":
        player["hunger"] += item.get("hunger_restore", 0)
        if player["hunger"] > player["max_hunger"]:
            player["hunger"] = player["max_hunger"]
        print(f"Vous mangez : {item['name']} (+{item['hunger_restore']} Faim)")
        print(f"Faim : {player['hunger']}/{player['max_hunger']}")

        # Retirer de l'inventaire
        remove_from_inventory(item)
        return True

    return False

def apply_item_stats(item):
    """Applique les stats d'un item au joueur"""
    item_type = item.get("type")

    if item_type == "weapon":
        player["attack"] += item.get("attack", 0)
        print(f"  +{item.get('attack', 0)} Attaque → Total : {player['attack']}")
    elif item_type == "armor":
        player["defense"] += item.get("defense", 0)
        print(f"  +{item.get('defense', 0)} Défense → Total : {player['defense']}")


def remove_item_stats(item):
    """Retire les stats d'un item du joueur"""
    item_type = item.get("type")

    if item_type == "weapon":
        player["attack"] -= item.get("attack", 0)
        print(f"  -{item.get('attack', 0)} Attaque → Total : {player['attack']}")
    elif item_type == "armor":
        player["defense"] -= item.get("defense", 0)
        print(f"  -{item.get('defense', 0)} Défense → Total : {player['defense']}")
