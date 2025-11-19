# ============================================================
# CONFIG
# ============================================================
ACTIONS = ["Chat with Keeper", "Accept a Quest", "Get Drunk"]

# Outcome probabilities
ACTION_OUTCOMES = {
    "Chat with Keeper": {
        "outcomes": [
            "Keeper encourages you (+10 mood)",
            "Keeper discourages you (-10 mood)",
            "Receive a gift from Keeper",
            "Fight the Keeper"
        ],
        "probs": [0.5, 0.15, 0.3, 0.05]
    },
    "Accept a Quest": {
        "outcomes": [
            "Fight a Dragon",
            "Defend a Caravan",
            "Clean the Hero Statue"
        ],
        "probs": [0.1, 0.7, 0.2]
    },
    "Get Drunk": {
        "outcomes": [
            "Lose 0.5 money",
            "Lose 0.2 health",
            "Gain +20 mood"
        ],
        "probs": [0.4, 0.4, 0.2]
    }
}

SECONDARY_OUTCOMES = {
    "Receive a gift from Keeper": {
        "outcomes": ["+20 money", "Health potion +10 health"],
        "probs": [0.5, 0.5]
    },
    "Fight the Keeper": {
        "outcomes": ["+10 money", "Nothing happens", "-20 health"],
        "probs": [0.1, 0.3, 0.6]
    },
    "Fight a Dragon": {
        "outcomes": ["Slay the dragon +50 money", "Die -100 health", "Retreat -30 health"],
        "probs": [0.5, 0.1, 0.4]
    },
    "Defend a Caravan": {
        "outcomes": ["Protect the caravan +20 money", "Abandon caravan -10 health"],
        "probs": [0.5, 0.5]
    },
    "Clean the Hero Statue": {
        "outcomes": ["Cleaned +10 money", "Blessed by the statue +10 health"],
        "probs": [0.9, 0.1]
    }
}

