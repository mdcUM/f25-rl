from typing import Dict, Any, List
from memory import CharacterMemory


# ============================================================
# NPC CLASS
# ============================================================
class NPC:
    def __init__(self, name="Aldric", traits=["curious"], health=100.0, money=20.0, mood=50.0):
        self.name = name
        self.traits = traits
        self.health = health
        self.money = money
        self.mood = mood
        self.last_report = "Woke up in the tavern."
        self.decision_log: List[Dict[str, Any]] = []     # decision history
        self.trust = 0

        # Persistent memory system
        self.memory = CharacterMemory(name, f"{name.lower()}_state.json")
        self.short_term_memory = self.memory.short_term

    def state(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "traits": self.traits,
            "health": self.health,
            "money": self.money,
            "mood": self.mood
        }

    def adjust_state(self, effect: str):
        if "+10 mood" in effect:
            self.mood = min(100, self.mood + 10)
        elif "-10 mood" in effect:
            self.mood = max(0, self.mood - 10)
        elif "+20 mood" in effect:
            self.mood = min(100, self.mood + 20)
        elif "Lose 0.2 health" in effect:
            self.health = max(0, self.health - 20)
        elif "Lose 0.5 money" in effect:
            self.money = max(0, self.money * 0.5)
        elif "+20 money" in effect:
            self.money += 20
        elif "+10 money" in effect:
            self.money += 10
        elif "+50 money" in effect:
            self.money += 50
        elif "-10 health" in effect:
            self.health = max(0, self.health - 10)
        elif "-20 health" in effect:
            self.health = max(0, self.health - 20)
        elif "-30 health" in effect:
            self.health = max(0, self.health - 30)
        elif "+10 health" in effect:
            self.health = min(100, self.health + 10)
        elif "Die" in effect:
            self.health = 0

    def alive(self) -> bool:
        return self.health > 0

    def won(self) -> bool:
        return self.money >= 150

