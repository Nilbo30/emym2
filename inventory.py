"""
Gestion de l'inventaire du joueur avec système de slots d'équipement
"""

# Inventaire du joueur (liste d'objets)
inventory = []

# Limite de taille
MAX_INVENTORY_SIZE = 20


def add_to_inventory(item):
    """
    Ajoute un objet à l'inventaire.
    Retourne True si réussi, False si inventaire plein.
    """
    if len(inventory) >= MAX_INVENTORY_SIZE:
        print(f"Inventaire plein ! ({MAX_INVENTORY_SIZE}/{MAX_INVENTORY_SIZE})")
        return False

    if "equipped" not in item:
        item["equipped"] = False
    if "equipped_slot" not in item:
        item["equipped_slot"] = None

    inventory.append(item)
    print(f"Ajouté à l'inventaire : {item['name']}")
    print(f"Inventaire : {len(inventory)}/{MAX_INVENTORY_SIZE}")
    return True


def remove_from_inventory(item):
    """Retire un objet de l'inventaire"""
    if item in inventory:
        # Si l'item est équipé, le déséquiper d'abord
        if item.get("equipped"):
            from player import unequip_slot
            slot = item.get("equipped_slot")
            if slot:
                unequip_slot(slot)
        inventory.remove(item)
        return True
    return False


def get_inventory():
    """Retourne l'inventaire actuel"""
    return inventory


def clear_inventory():
    """Vide complètement l'inventaire (pour game over)"""
    global inventory
    inventory = []


def is_equipped(item):
    """Vérifie si un item est équipé"""
    return item.get("equipped", False)


def equip_item(item):
    """
    Équipe un item dans son slot approprié.
    Gère le remplacement automatique.
    """
    from player import get_valid_slot_for_item, equip_to_slot

    slot = get_valid_slot_for_item(item)
    if slot is None:
        print(f"Impossible d'équiper : {item['name']}")
        return False

    old_item = equip_to_slot(item, slot)
    if old_item:
        print(f"Remplacé : {old_item['name']}")
    print(f"Équipé : {item['name']} → [{slot}]")
    return True


def unequip_item(item):
    """Déséquipe un item"""
    from player import unequip_slot

    slot = item.get("equipped_slot")
    if slot and item.get("equipped"):
        unequip_slot(slot)
        print(f"Déséquipé : {item['name']}")
        return True
    return False


def print_inventory():
    """Affiche l'inventaire dans la console (pour debug)"""
    print("\n=== INVENTAIRE ===")
    if not inventory:
        print("(vide)")
    else:
        for i, item in enumerate(inventory):
            slot_info = f" [{item['equipped_slot']}]" if item.get("equipped") else ""
            print(f"{i+1}. {item['name']} ({item['type']}){slot_info}")
    print(f"Total : {len(inventory)}/{MAX_INVENTORY_SIZE}")
    print("==================\n")
