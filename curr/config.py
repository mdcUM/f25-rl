# config.py
# ============================================================
# CONFIG - EXPANDED STORY VERSION
# ============================================================

# ============================================================
# WORLD CONTEXT
# ============================================================
WORLD_CONTEXT = """
The Year of the Golden Anvil - A time of unrest in the kingdom of Valdoria.

THE SETTING: You reside in the Rusty Flagon, a weathered tavern on the edge of the Whispering Woods. 
The tavern keeper, Mira, knows everyone's secrets. Merchants pass through seeking guards. 
Rumors speak of a dragon in the northern peaks, bandits on the trade roads, and an ancient curse 
on the Hero's Statue in the town square.

THE STAKES: The kingdom teeters on the brink. Those with coin and courage may shape its future.
"""

# ============================================================
# ACTIONS & OUTCOMES
# ============================================================
ACTIONS = [
    "Chat with Keeper", 
    "Accept a Quest", 
    "Get Drunk",
    "Visit the Marketplace",
    "Explore the Woods"
]

ACTION_OUTCOMES = {
    "Chat with Keeper": {
        "outcomes": [
            "Mira shares encouraging words (+10 mood)",
            "Mira warns you about danger (-10 mood)",
            "Mira offers you a gift",
            "You insult Mira and she throws you out (Fight the Keeper)",
            "Mira shares a dark rumor",
            "Mira offers you a mysterious map"
        ],
        "probs": [0.30, 0.15, 0.20, 0.05, 0.20, 0.10]
    },
    
    "Accept a Quest": {
        "outcomes": [
            "Hunt the Northern Dragon",
            "Defend a Merchant Caravan",
            "Clean the Cursed Hero Statue",
            "Investigate the Abandoned Mine",
            "Retrieve a Stolen Heirloom",
            "Escort a Noble Through Bandit Territory"
        ],
        "probs": [0.08, 0.35, 0.15, 0.15, 0.17, 0.10]
    },
    
    "Get Drunk": {
        "outcomes": [
            "You gamble away half your coin (Lose 0.5 money)",
            "You start a brawl (Lose 0.2 health)",
            "You have a wonderful time (+20 mood)",
            "You meet a mysterious stranger",
            "You pass out and wake up robbed (-15 money)",
            "You overhear a valuable secret (+10 mood)"
        ],
        "probs": [0.25, 0.20, 0.25, 0.15, 0.10, 0.05]
    },
    
    "Visit the Marketplace": {
        "outcomes": [
            "You find a merchant selling supplies",
            "You get pickpocketed (-10 money)",
            "You win at a street game (+15 money)",
            "You meet an old friend",
            "You witness a public execution",
            "You discover a black market"
        ],
        "probs": [0.30, 0.15, 0.20, 0.15, 0.10, 0.10]
    },
    
    "Explore the Woods": {
        "outcomes": [
            "You encounter bandits",
            "You find medicinal herbs (+15 health)",
            "You discover an ancient shrine",
            "You get lost and waste time (-5 mood)",
            "You find a hidden cache of supplies",
            "You meet a mysterious hermit"
        ],
        "probs": [0.25, 0.25, 0.15, 0.15, 0.10, 0.10]
    }
}

SECONDARY_OUTCOMES = {
    # Keeper interactions
    "Mira offers you a gift": {
        "outcomes": [
            "Gold coins from her savings (+25 money)",
            "A healing potion from her cellar (+15 health)",
            "An old map to a treasure site (+10 mood)",
            "A lucky charm that boosts confidence (+20 mood)"
        ],
        "probs": [0.40, 0.30, 0.15, 0.15]
    },
    
    "Fight the Keeper": {
        "outcomes": [
            "You win but feel guilty (+10 money, -10 mood)",
            "Stalemate - you both back down (Nothing happens)",
            "She beats you soundly (-25 health)",
            "Town guards intervene (-20 money fine)"
        ],
        "probs": [0.10, 0.30, 0.40, 0.20]
    },
    
    "Mira shares a dark rumor": {
        "outcomes": [
            "The dragon has been seen near the village (-5 mood)",
            "The king is dying and nobles plot (+5 mood, knowledge gained)",
            "Bandits plan to raid the tavern next week (-10 mood)",
            "A plague spreads in the eastern provinces (-5 mood)"
        ],
        "probs": [0.30, 0.25, 0.25, 0.20]
    },
    
    "Mira offers you a mysterious map": {
        "outcomes": [
            "Map leads to bandit hideout (future quest unlocked)",
            "Map shows secret passage through mountains (+10 mood)",
            "Map is a fake, Mira was testing you (-5 mood)",
            "Map reveals location of ancient artifact (+15 mood)"
        ],
        "probs": [0.30, 0.30, 0.20, 0.20]
    },
    
    # Quest outcomes
    "Hunt the Northern Dragon": {
        "outcomes": [
            "You slay the beast and claim its hoard (+80 money, +20 mood)",
            "The dragon incinerates you (Die -100 health)",
            "You wound it but must retreat (-35 health, +5 mood)",
            "You discover the dragon guards an ancient secret (+30 money, +10 mood)",
            "You negotiate with the dragon - it spares you for tribute (-30 money, +20 mood)"
        ],
        "probs": [0.25, 0.10, 0.30, 0.15, 0.20]
    },
    
    "Defend a Merchant Caravan": {
        "outcomes": [
            "Bandits flee, merchant rewards you generously (+35 money)",
            "You're ambushed - barely escape alive (-15 health, +10 money)",
            "Successful defense, standard payment (+20 money)",
            "Bandits were too strong, you abandon the caravan (-10 health, -5 mood)",
            "You discover the merchant smuggles illegal goods (moral dilemma, +15 money)"
        ],
        "probs": [0.20, 0.20, 0.30, 0.15, 0.15]
    },
    
    "Clean the Cursed Hero Statue": {
        "outcomes": [
            "The curse lifts, townspeople celebrate (+15 money, +15 mood)",
            "The statue blesses you with vitality (+20 health, +10 mood)",
            "Cleaning reveals an inscription with a treasure clue (+10 mood)",
            "The curse affects you during cleaning (-10 health, +10 money)",
            "You find offerings left at the statue (+12 money)"
        ],
        "probs": [0.25, 0.20, 0.20, 0.15, 0.20]
    },
    
    "Investigate the Abandoned Mine": {
        "outcomes": [
            "You find valuable ore (+25 money)",
            "The mine collapses on you (-30 health)",
            "You encounter hostile creatures (-20 health, +10 money)",
            "You discover why it was abandoned - nothing of value (Nothing happens)",
            "You find an ancient dwarven artifact (+40 money, +10 mood)",
            "You meet survivors hiding from the war (+10 mood)"
        ],
        "probs": [0.25, 0.10, 0.20, 0.15, 0.15, 0.15]
    },
    
    "Retrieve a Stolen Heirloom": {
        "outcomes": [
            "You recover it and earn a noble's favor (+30 money, +15 mood)",
            "The thief ambushes you (-15 health, -10 money)",
            "You track down the thief and recover the item (+25 money)",
            "The heirloom is cursed - you're affected (-10 health, +20 money)",
            "You find the heirloom but learn a dark family secret (+20 money, -5 mood)"
        ],
        "probs": [0.30, 0.15, 0.25, 0.15, 0.15]
    },
    
    "Escort a Noble Through Bandit Territory": {
        "outcomes": [
            "Safe passage, generous reward (+40 money, +10 mood)",
            "Ambushed - you're wounded protecting them (-25 health, +35 money)",
            "The noble is ungrateful and pays poorly (+10 money, -5 mood)",
            "You're betrayed - the noble was bait for bandits (-30 health, -15 money)",
            "You and the noble bond over the journey (+25 money, +15 mood)"
        ],
        "probs": [0.30, 0.20, 0.20, 0.10, 0.20]
    },
    
    # Drinking outcomes
    "You meet a mysterious stranger": {
        "outcomes": [
            "They offer you a dangerous job (+15 mood)",
            "They warn you about an upcoming threat (+5 mood)",
            "They try to recruit you for a rebellion (+10 mood)",
            "They're actually a noble in disguise (+20 money, +10 mood)",
            "They challenge you to a drinking contest (Lose 0.2 health, +10 mood)"
        ],
        "probs": [0.25, 0.25, 0.20, 0.15, 0.15]
    },
    
    # Marketplace outcomes
    "You find a merchant selling supplies": {
        "outcomes": [
            "You buy healing supplies (spend 15 money, +20 health)",
            "You buy information about a treasure (spend 10 money, +5 mood)",
            "Prices are too high, you leave empty-handed (Nothing happens)",
            "You haggle successfully and get a great deal (spend 5 money, +15 health)"
        ],
        "probs": [0.35, 0.25, 0.20, 0.20]
    },
    
    "You meet an old friend": {
        "outcomes": [
            "They lend you money (+15 money, +10 mood)",
            "They ask you for help with a problem (+5 mood, future quest)",
            "You catch up and share a meal (+15 mood)",
            "They owe you money and finally repay you (+20 money, +5 mood)"
        ],
        "probs": [0.30, 0.25, 0.30, 0.15]
    },
    
    "You witness a public execution": {
        "outcomes": [
            "The condemned speaks of hidden treasure before death (+5 mood)",
            "You're deeply disturbed by the brutality (-15 mood)",
            "You recognize the criminal - they were innocent (-20 mood)",
            "The crowd's bloodlust frightens you (-10 mood)"
        ],
        "probs": [0.15, 0.35, 0.25, 0.25]
    },
    
    "You discover a black market": {
        "outcomes": [
            "You buy forbidden supplies (spend 20 money, +15 health, +5 mood)",
            "You're caught by guards and fined (-25 money)",
            "You find valuable information for sale (+10 mood, knowledge gained)",
            "You meet a fence who offers to buy stolen goods (+15 money)"
        ],
        "probs": [0.30, 0.20, 0.30, 0.20]
    },
    
    # Woods outcomes
    "You encounter bandits": {
        "outcomes": [
            "You fight them off but are wounded (-20 health, +10 money)",
            "You flee and escape unharmed (-5 mood)",
            "You're robbed at knifepoint (-25 money, -10 health)",
            "You intimidate them and they flee (+15 mood)",
            "You join forces temporarily and split loot (+20 money, -5 mood)"
        ],
        "probs": [0.25, 0.20, 0.20, 0.15, 0.20]
    },
    
    "You discover an ancient shrine": {
        "outcomes": [
            "You pray and feel blessed (+20 mood)",
            "The shrine grants you mystical healing (+25 health)",
            "You find offerings left by others (+15 money)",
            "The shrine is trapped - you trigger it (-15 health)",
            "You have a vision of your future (+10 mood, knowledge gained)"
        ],
        "probs": [0.30, 0.25, 0.20, 0.10, 0.15]
    },
    
    "You find a hidden cache of supplies": {
        "outcomes": [
            "Gold and provisions (+30 money)",
            "Medical supplies and food (+20 health)",
            "Weapons and armor you can sell (+25 money)",
            "The cache is booby-trapped (-20 health, +15 money)"
        ],
        "probs": [0.40, 0.30, 0.20, 0.10]
    },
    
    "You meet a mysterious hermit": {
        "outcomes": [
            "They teach you survival skills (+10 health, +5 mood)",
            "They share wisdom about the kingdom (+15 mood)",
            "They're actually a wanted criminal and attack you (-25 health)",
            "They offer you a magical trinket (+20 mood)",
            "They ask you to deliver a message to town (+10 money, future quest)"
        ],
        "probs": [0.30, 0.25, 0.10, 0.20, 0.15]
    }
}