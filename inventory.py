"""
Gestion de l'inventaire du joueur
"""

# Inventaire du joueur (liste d'objets)
inventory = []

# Limite de taille (pour l'instant)
MAX_INVENTORY_SIZE = 20


def add_to_inventory(item):
    """
    Ajoute un objet à l'inventaire
    Retourne True si réussi, False si inventaire plein
    """
    if len(inventory) >= MAX_INVENTORY_SIZE:
        print(f"Inventaire plein ! ({MAX_INVENTORY_SIZE}/{MAX_INVENTORY_SIZE})")
        return False

    # Ajouter le champ "equipped" si pas déjà présent
    if "equipped" not in item:
        item["equipped"] = False  # ← AJOUTE CETTE LIGNE

    inventory.append(item)
    print(f"Ajouté à l'inventaire : {item['name']}")
    print(f"Inventaire : {len(inventory)}/{MAX_INVENTORY_SIZE}")
    return True


def remove_from_inventory(item):
    """
    Retire un objet de l'inventaire
    """
    if item in inventory:
        inventory.remove(item)
        return True
    return False


def get_inventory():
    """
    Retourne l'inventaire actuel
    """
    return inventory


def clear_inventory():
    """
    Vide complètement l'inventaire (pour game over)
    """
    global inventory
    inventory = []


def print_inventory():
    """
    Affiche l'inventaire dans la console (pour debug)
    """
    print("\n=== INVENTAIRE ===")
    if not inventory:
        print("(vide)")
    else:
        for i, item in enumerate(inventory):
            equipped_status = "⚔️ ÉQUIPÉ" if item.get("equipped", False) else ""  # ← AJOUTE
            print(f"{i+1}. {item['name']} ({item['type']}) {equipped_status}")
            print(f"{i+1}. {item['name']} ({item['type']})")
    print(f"Total : {len(inventory)}/{MAX_INVENTORY_SIZE}")
    print("==================\n")

def equip_item(item):
    """
    Marque un item comme équipé
    Déséquipe automatiquement l'item du même type si nécessaire
    """
    from game_logic import apply_item_stats, remove_item_stats

    item_type = item.get("type")

    # Si c'est une arme ou une armure, déséquiper l'ancien du même type
    if item_type in ["weapon", "armor"]:
        for inv_item in inventory:
            if inv_item.get("equipped") and inv_item.get("type") == item_type:
                # IMPORTANT : Retirer les stats de l'ancien item
                remove_item_stats(inv_item)  # ← NOUVEAU
                inv_item["equipped"] = False  # Déséquiper l'ancien
                print(f"Déséquipé : {inv_item['name']}")

    # Équiper le nouvel item
    item["equipped"] = True

    # Appliquer les stats du nouvel item
    apply_item_stats(item)  # ← NOUVEAU

    print(f"Équipé : {item['name']}")

def unequip_item(item):
    """Déséquipe un item"""
    if item.get("equipped"):
        item["equipped"] = False
        print(f"Déséquipé : {item['name']}")
        return True
    return False


def is_equipped(item):
    """Vérifie si un item est équipé"""
    return item.get("equipped", False)
