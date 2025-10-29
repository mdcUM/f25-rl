import json, random, re, os
import ollama
from typing import Dict, List, Any

# ============================================================
# Context Classes
# ============================================================


class SceneContext:
    """Describes the environment and possible actions."""

    def __init__(
        self, location: str, objects: List[str], actions: Dict[str, List[str]]
    ):
        self.location = location
        self.objects = objects
        self.actions = actions  # {"buy":["apple"],"talk":["merchant"],"move":["north"]}

    def get_affordances(self):
        return [(a, o) for a, objs in self.actions.items() for o in objs]

    def __repr__(self):
        return f"<Scene {self.location} | {list(self.actions.keys())}>"


class CharacterContext:
    """Long-term traits + short-term runtime state, persisted in JSON."""

    def __init__(self, name: str, file_path: str):
        self.name = name
        self.file_path = file_path
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
        else:
            data = {
                "traits": {"curiosity": 0.5, "greed": 0.3},
                "goals": ["explore the world"],
                "memory": [],
            }

        # Long-term, persistent attributes
        self.traits = data["traits"]
        self.goals = data["goals"]
        self.memory = data["memory"]

        # Short-term (transient, not saved to disk)
        self.short_term: dict[str, any] = {
            "last_reward": 0.0,
            "emotion": "neutral",
        }

    def remember(self, event: str):
        """Append an event to long-term memory and persist it."""
        self.memory.append(event)
        if len(self.memory) > 10:
            self.memory.pop(0)
        self.save()

    def update_short_term(self, key: str, value: any):
        """Update temporary (non-persistent) runtime state."""
        self.short_term[key] = value

    def save(self):
        """Persist only long-term memory, traits, and goals."""
        with open(self.file_path, "w") as f:
            json.dump(
                {
                    "traits": self.traits,
                    "goals": self.goals,
                    "memory": self.memory,
                },
                f,
                indent=2,
            )

    def __repr__(self):
        return f"<Character {self.name} | traits={self.traits}, short_term={self.short_term}>"


class PlotContext:
    def __init__(self):
        self.events = []

    def add_event(self, event: str):
        self.events.append(event)

    def summarize(self) -> str:
        if not self.events:
            return "No events yet."
        return " → ".join(self.events[-5:])

    def __repr__(self):
        return f"<Plot len={len(self.events)}>"


# ============================================================
# Gemma-powered Policy
# ============================================================


class LLMCharacterPolicy:
    """Uses local Ollama model (Gemma 2B) to decide, narrate, and self-edit memory."""

    def __init__(self, model="gemma:2b"):
        self.model = model

    def chat(self, prompt: str) -> str:
        r = ollama.chat(
            model=self.model,
            options={"temperature": 0.8, "top_p": 0.9},
            messages=[{"role": "user", "content": prompt}],
        )
        return r["message"]["content"]

    def select_and_update(
        self, scene: SceneContext, char: CharacterContext, plot: PlotContext
    ) -> (str, str):
        last_action = char.memory[-1] if char.memory else "None"
        last_reward = char.short_term.get("last_reward", 0)

        prompt = f"""
You are {char.name}, a character in an evolving story simulation.
Last action: {last_action}

Scene:
- Location: {scene.location}
- Objects: {scene.objects}
- Possible actions: {scene.actions}

Your JSON state (editable and persistent between turns):
{json.dumps({"traits": char.traits, "goals": char.goals, "memory": char.memory[-5:]}, indent=2)}

Plot so far: {plot.summarize()}

Reflect on your previous choice and continue the story. 
Describe what happens next as a short paragraph of narrative text.
Decide your next action from the available options, choosing options based on how new they are.
Do not choose the same action repeatedly unless it makes sense. 

Respond STRICTLY as JSON in this format:
{{
  "action": "<verb>",
  "target": "<object>",
  "story": "<narrative paragraph>",
  "updated_state": {{
    "traits": {{...}},
    "goals": [...],
    "memory": [...]
  }}
}}
"""
        text = self.chat(prompt)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            print("(Model output unparseable, picking random action.)")
            return random.choice(scene.get_affordances())
        try:
            data = json.loads(match.group())
            story = data.get("story", "").strip()
            if story:
                print("\n" + story + "\n")

            us = data.get("updated_state", {})
            # if "traits" in us:
            #     char.traits = us["traits"]
            # if "goals" in us:
            #     char.goals.extend(us["goals"])
            if "memory" in us:
                char.memory.extend(us["memory"])
            char.save()

            return (data["action"], data["target"])
        except Exception as e:
            print(f"(Parsing error: {e})")
            return random.choice(scene.get_affordances())


# ============================================================
# Game Loop
# ============================================================


class GameLoop:
    def __init__(self, scene, character, plot, policy):
        self.scene = scene
        self.character = character
        self.plot = plot
        self.policy = policy

    def step(self):
        action = self.policy.select_and_update(self.scene, self.character, self.plot)
        event = f"{self.character.name} performs {action[0]} on {action[1]} in {self.scene.location}"
        print(f"Action: {event}")
        # self.character.remember(event)
        self.plot.add_event(event)
        print(f"Plot summary: {self.plot.summarize()}\n")


# ============================================================
# Run Example
# ============================================================

if __name__ == "__main__":
    scene_marketplace = SceneContext(
        "market_square",
        ["apple", "bread", "merchant", "beggar", "guard", "fountain"],
        {
            "buy": ["apple", "bread"],
            "talk": ["merchant", "beggar", "guard"],
            "give": ["beggar"],
            "inspect": ["fountain", "stall"],
        },
    )

    char = CharacterContext("Cyrus", "cyrus_state.json")
    plot = PlotContext()
    policy = LLMCharacterPolicy("gemma:2b")
    game = GameLoop(scene_marketplace, char, plot, policy)

    for _ in range(3):
        game.step()
