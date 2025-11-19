import json, random, os, time, re
import ollama
from typing import Dict, Any, List

# ============================================================
# CONFIG
# ============================================================
ACTIONS = ["Chat with Keeper", "Accept a Quest", "Get Drunk"]

ACTION_OUTCOMES = {
    "Chat with Keeper": {
        "outcomes": [
            "Keeper encourages you (+10 mood)",
            "Keeper discourages you (-10 mood)",
            "Receive a gift from Keeper",
            "Fight the Keeper"
        ],
        "outcome_vals": [
            {
            "mood": 10,
            "health": 0,
            "money": 0
            },
            {
            "mood": -10,
            "health": 0,
            "money": 0
            },
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

        #self.short_term_memory = ShortTermMemory()
        #self.short_term = {"last_reward": 0.0, "emotion": "neutral"}

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
        self.decision_log: List[Dict[str, Any]] = []

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


# ============================================================
# OLLAMA INTERFACE
# ============================================================
def ollama_chat(prompt: str, model="llama3.1", temperature: float = 0.9):
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature}
        )
        return response["message"]["content"].strip()
    except Exception as e:
        print(f"LLM error: {e}")
        return "Get Drunk"


# ============================================================
# ACTION LOGIC
# ============================================================
def perform_action(npc: NPC, action: str) -> str:
    base = ACTION_OUTCOMES[action]
    outcome = random.choices(base["outcomes"], weights=base["probs"], k=1)[0]
    npc.adjust_state(outcome)

    if outcome in SECONDARY_OUTCOMES:
        sec = SECONDARY_OUTCOMES[outcome]
        sub_outcome = random.choices(sec["outcomes"], weights=sec["probs"], k=1)[0]
        npc.adjust_state(sub_outcome)
        outcome = f"{outcome} → {sub_outcome}"

    npc.memory.remember(action, outcome)
    npc.short_term_memory.add(f"{action} → {outcome}")
    npc.memory.short_term = npc.short_term_memory  # keep CharacterMemory in sync
    npc.memory.save()  

    return outcome


# ============================================================
# LLM DECISIONS
# ============================================================
def choose_action_llm(npc: NPC) -> str:
    available_actions = ["Chat with Keeper", "Get Drunk"]
    if npc.mood > 50 and npc.health > 60:
        available_actions.append("Accept a Quest")

    action_list = ", ".join(available_actions)

    prompt = f"""
You are roleplaying {npc.name}, a {', '.join(npc.traits)} adventurer resting in a medieval tavern.

Your long-term goals: {npc.memory.goals}.
Recent memories: {npc.memory.summarize()}.
Short-term events: {npc.short_term_memory.recent_events}.

You may choose ONE of the following actions today: {action_list}.

Your current state:
Health={npc.health}, Money={npc.money}, Mood={npc.mood}

Decision rules:
- If health is low (<40), avoid dangerous or strenuous activities.
- If money is low (<50), prioritize quests or ways to earn gold.
- If mood is low (<40), choose actions that can raise it.
- You are curious and impulsive, so you may occasionally take risks.

Respond ONLY with one of the available actions exactly as written: {action_list}.
"""
    response = ollama_chat(prompt, temperature=0.9)
    for act in available_actions:
        if act.lower() in response.lower():
            return act
    return "Chat with Keeper"


def describe_day_llm(npc: NPC, action: str, event: str) -> str:
    """Generate the immersive daily report and store a short summary in memory."""
    prompt = f"""
Write a short (2-3 sentence) medieval-style journal entry describing the day of {npc.name}.
Today's action: {action}.
Outcome: {event}.
Recent memories: {npc.memory.summarize()}.
Short-term events: {npc.short_term_memory.recent_events}.
Long-term goals: {npc.memory.goals}.
NPC State at end: Health={npc.health}, Money={npc.money}, Mood={npc.mood}.
Keep it immersive and in-character.
"""
    report = ollama_chat(prompt)
    npc.last_report = report
    return report


def adjust_mood_llm(npc: NPC) -> None:
    prompt = f"""
NPC current state: {npc.state()}.
Yesterday's report: {npc.last_report}.
Based on the events, how should mood adjust (-10 to +10)? Respond with a single integer.
"""
    response = ollama_chat(prompt)
    try:
        mood_change = int(re.findall(r"-?\d+", response)[0])
        npc.mood = max(0, min(100, npc.mood + mood_change))
    except:
        pass


def reflect_llm(npc: NPC):
    """Every few days, let the NPC update goals or reflect."""
    prompt = f"""
You are {npc.name}, reflecting on your recent adventures and memories:
{npc.memory.summarize()}.
Current goals: {npc.memory.goals}.
Based on your experiences, suggest any goal or mindset adjustments (if any).
Respond as JSON: {{ "goals": [...], "reflection": "<short text>" }}
"""
    resp = ollama_chat(prompt)
    match = re.search(r"\{.*\}", resp, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            npc.memory.goals = data.get("goals", npc.memory.goals)
            npc.memory.remember(f"Reflection: {data.get('reflection', '')}")
            npc.memory.save()
        except:
            pass


# ============================================================
# MAIN SIMULATION LOOP
# ============================================================
def run_simulation(days: int = 10):
    npc = NPC()
    print(f"=== Beginning Simulation with {npc.name} ===")

    for day in range(1, days + 1):
        print(f"\n--- DAY {day} ---")

        adjust_mood_llm(npc)
        if not npc.alive():
            print("NPC has died. Simulation ends.")
            break

        action = choose_action_llm(npc)
        print(f"Chosen action: {action}")

        event = perform_action(npc, action)
        print(f"Outcome: {event}")

        eod_report = describe_day_llm(npc, action, event)
        print(f"Report:\n{eod_report}")

        npc.last_report = eod_report
        npc.decision_log.append({
            "day": day,
            "action": action,
            "outcome": event,
            "state": npc.state(),
        })

        if npc.won():
            print(f"{npc.name} has achieved wealth and wins the game!")
            break
        if not npc.alive():
            print(f"{npc.name} has died. Final State: {npc.state()}")
            break

        if day % 3 == 0:
            reflect_llm(npc)

        time.sleep(1)

    print("\n=== End of Simulation ===")
    print(json.dumps(npc.decision_log, indent=2))


if __name__ == "__main__":
    run_simulation(10)
