# Fish System Implementation

## Phase 6: Quality and Rarity Systems

### 6.1 Fish Database and Spawning
```python
# Fish Database
FISH_DATABASE = {
    "Common": ["Cod", "Carp", "Minnow", "Perch", "Sunfish", "Tilapia", "Catfish", 
               "Goldfish", "Bluegill", "Troutlet"],
    "Uncommon": ["Rainbow Trout", "Bass", "Pike", "Mackerel", "Flounder", 
                "Walleye", "Rockfish", "Perch King", "Small Snapper", "Eel"],
    "Rare": ["Salmon", "Swordfish", "Barracuda", "Marlin", "Bluefin Tuna",
             "Sturgeon", "Grouper", "Lionfish", "Golden Trout", "Red Snapper"],
    "Epic": ["Anglerfish", "Giant Catfish", "Ocean Sunfish", "Tarpon",
             "King Mackerel", "Giant Salmon", "Peacock Bass", "Rainbow Marlin",
             "Electric Eel", "Swordfin"],
    "Legendary": ["Kraken Carp", "Mythical Koi", "Leviathan Cod", "Golden Barracuda",
                  "Celestial Tuna", "Phantom Marlin", "Titan Sturgeon", "Dragonfish",
                  "Aurora Salmon", "Poseidon's Pike"]
}

# Rarity Chances
RARITY_CHANCES_NORMAL = {"Common": 0.65, "Uncommon": 0.20, "Rare": 0.10, "Epic": 0.04, "Legendary": 0.01}
RARITY_CHANCES_CHEAT = {"Legendary": 0.65, "Epic": 0.20, "Uncommon": 0.10, "Common": 0.04, "Rare": 0.01}

# Base Prices
BASE_PRICES = {"Common": 10, "Uncommon": 25, "Rare": 50, "Epic": 100, "Legendary": 250}

def calculate_quality(stage_scores):
    """Calculate fish quality based on stage scores"""
    quality = sum(stage_scores) / len(stage_scores)
    
    if quality >= 90:
        return "Perfect"
    elif quality >= 70:
        return "Great"
    elif quality >= 40:
        return "Fine"
    elif quality >= 10:
        return "Rough"
    else:
        return "Trash"

def spawn_fish(rod_luck, cheat_mode):
    """Spawn a fish based on rarity probabilities"""
    base_chances = RARITY_CHANCES_CHEAT if cheat_mode else RARITY_CHANCES_NORMAL
    
    # Adjust probabilities based on rod luck
    luck_bonus = rod_luck / 1000
    adjusted_chances = {}
    
    for rarity, chance in base_chances.items():
        if rarity in ["Rare", "Epic", "Legendary"]:
            adjusted_chances[rarity] = min(0.8, chance + luck_bonus)
        else:
            adjusted_chances[rarity] = max(0.01, chance - luck_bonus * 0.5)
    
    # Normalize probabilities
    total = sum(adjusted_chances.values())
    for rarity in adjusted_chances:
        adjusted_chances[rarity] /= total
    
    # Select rarity
    random_value = random.random()
    cumulative = 0
    selected_rarity = "Common"
    for rarity, chance in adjusted_chances.items():
        cumulative += chance
        if random_value <= cumulative:
            selected_rarity = rarity
            break
    
    # Select specific fish from rarity
    fish_name = random.choice(FISH_DATABASE[selected_rarity])
    return {"name": fish_name, "rarity": selected_rarity}

def calculate_selling_price(fish_rarity, quality_percentage):
    """Calculate selling price based on fish rarity and quality"""
    base_price = BASE_PRICES[fish_rarity]
    quality_multiplier = quality_percentage / 100
    return int(base_price * (quality_multiplier ** 1.5))
```

## Phase 4: Shop System

### 4.1 Shop Interface
```python
# Rod Upgrades
ROD_UPGRADES = {
    "Novice Rod": {"price": 300, "luck": 20},
    "Master Rod": {"price": 1000, "luck": 45}
}

def handle_shop_purchase(events, current_rod, gold):
    """Handle rod purchases in shop"""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and current_rod != "Novice Rod":
                if gold >= ROD_UPGRADES["Novice Rod"]["price"]:
                    return "Novice Rod", gold - ROD_UPGRADES["Novice Rod"]["price"]
            elif event.key == pygame.K_2 and current_rod != "Master Rod":
                if gold >= ROD_UPGRADES["Master Rod"]["price"]:
                    return "Master Rod", gold - ROD_UPGRADES["Master Rod"]["price"]
    return current_rod, gold