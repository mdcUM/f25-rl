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

    def add_event(self, story: str):
        self.events.append(story)

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
    
    # 1. Have the model choose an action but nothing else
    # 2. Determine reward ourselves
    # Alternative: Give model in-game feedback from the event and have it return the reward itself
    # Example feedback: action has been picked too many times, certain in-game events that we can allow to randomly happen
    # 3. Have the model update memory/state and make story based on reward
    def select_and_update(
        self, scene: SceneContext, char: CharacterContext, plot: PlotContext
    ) -> (str, str, float):
        last_action = char.memory[-1] if char.memory else "None"
        last_reward = char.short_term.get("last_reward", 0)

        action_prompt = f"""
You are {char.name}, a character in an evolving story simulation.

Last action: {last_action}
Last reward: {last_reward}

Scene:
- Location: {scene.location}
- Objects: {scene.objects}
- Possible actions: {scene.actions}

Your JSON state (editable and persistent between turns):
{json.dumps({"traits": char.traits, "goals": char.goals, "memory": char.memory[-5:]}, indent=2)}

Plot so far: {plot.summarize()}

Based on your traits, goals, memory, and the evolving plot, choose your next action to complete. 
When deciding your action, you should have your long-term goal in mind. Repeating an action over and over is highly discouraged.
Given the plot summary, you are HIGHLY encouraged to choose an action that deviates from your previous actions.

Your action should have made a significant contribution to the plot and made steps towards your goal.
Respond STRICTLY as JSON in this format:
{{
  "action": "<verb>",
  "target": "<object>"
}}

"""
        text = self.chat(action_prompt)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            print("(Model output unparseable, picking random action.)")
            return random.choice(scene.get_affordances())
        try:
            data = json.loads(match.group())
            action_text = f"{char.name} performs {data["action"]} on {data["target"]} in {scene.location}"
        except Exception as e:
            print(f"(Parsing error: {e})")
            return random.choice(scene.get_affordances())

        reward = random.uniform(-5, 5)
        char.update_short_term("last_reward", reward)

        reward_prompt = f"""
You are {char.name}, a character in an evolving story simulation.

Scene:
- Location: {scene.location}
- Objects: {scene.objects}
- Possible actions: {scene.actions}

Your JSON state (editable and persistent between turns):
{json.dumps({"traits": char.traits, "goals": char.goals, "memory": char.memory[-5:]}, indent=2)}

You've taken the following action: {action_text}.
The action resulted in a reward of {reward}. The reward is a numerical value indicating how well the action contributed to your goals and the plot.

Given the action and reward, describe how the event occurred as a short paragraph of narrative text that a reader could enjoy.
It is crucial that your description of the action reflects our numerical reward. If the reward is negative, the action should have had negative consequences or failed to contribute meaningfully to your goals.

Respond STRICTLY as JSON in this format:
{{
  "story": "<narrative paragraph>",
  "updated_state": {{
    "traits": {{...}},
    "goals": [...],
    "memory": [...]
  }}
}}
"""
        text = self.chat(reward_prompt)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            print("(Model output unparseable, picking random action.)")
            return random.choice(scene.get_affordances())
        try:
            data = json.loads(match.group())
            # Natural language description of the character's new action
            story = data.get("story", "").strip()
            if story:
                print("\n" + story + "\n")

            us = data.get("updated_state", {})
            if "traits" in us:
                char.traits = us["traits"]
            if "goals" in us:
                char.goals = us["goals"]
            if "memory" in us:
                char.memory = us["memory"]
            char.save()

            return (action_text, story, reward)
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
        print(f"Action: {action[0]}")
        self.character.remember(action[0])
        self.plot.add_event(action[1] if len(action) > 1 else action[0])

        print("Reward:", action[2] if len(action) > 2 else 0)
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

    for _ in range(10):
        game.step()
