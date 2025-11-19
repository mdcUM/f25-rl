import json
import os
from typing import Dict, Any


# ============================================================
# MEMORY SYSTEM
# ============================================================
class CharacterMemory:
    """Handles persistent and short-term memory for an NPC."""

    def __init__(self, name: str, file_path: str):
        self.name = name
        self.file_path = file_path
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
        else:
            data = {
                "traits": {"curiosity": 0.6, "greed": 0.4},
                "goals": ["seek adventure", "earn wealth"],
                "memory": [],
                "short_term": {"recent_events": []},
            }

        self.traits = data["traits"]
        self.goals = data["goals"]
        self.memory = data["memory"]
        self.short_term = ShortTermMemory.from_dict(data.get("short_term", {}))

    def remember(self, action: str, outcome: str):
        """Add (action, outcome) summary to memory (keep last 5)."""
        entry = f"{action} → {outcome}"
        self.memory.append(entry)
        if len(self.memory) > 5:
            self.memory.pop(0)
        self.save()

    def summarize(self) -> str:
        if not self.memory:
            return "No memories yet."
        return " → ".join(self.memory[-5:])

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(
                {"traits": self.traits, "goals": self.goals, "memory": self.memory,
                "short_term": self.short_term.to_dict()},
                f,
                indent=2,
            )


class ShortTermMemory:
    def __init__(self, max_size=5):
        self.max_size = max_size
        self.recent_events = []

    def add(self, event: str):
        self.recent_events.append(event)
        # keep only last N
        if len(self.recent_events) > self.max_size:
            self.recent_events.pop(0)

    def to_dict(self):
        return {
            "recent_events": self.recent_events
        }

    @staticmethod
    def from_dict(data):
        stm = ShortTermMemory()
        stm.recent_events = data.get("recent_events", [])
        return stm

