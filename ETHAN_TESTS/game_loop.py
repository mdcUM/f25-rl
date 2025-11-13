import json, random, os, time, re
import ollama
from typing import Dict, Any, List

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

    def state(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "traits": self.traits,
            "health": self.health,
            "money": self.money,
            "mood": self.mood
        }

    def adjust_state(self, effect: str):
        """Apply numeric effects extracted from text outcomes."""
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
    """Wrapper to call Ollama model with error handling."""
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature}
        )
        return response["message"]["content"].strip()
    except Exception as e:
        print(f"LLM error: {e}")
        return "Get Drunk"  # fallback


# ============================================================
# ACTION LOGIC
# ============================================================
def perform_action(npc: NPC, action: str) -> str:
    """Simulate performing an action with probabilistic outcomes."""
    base = ACTION_OUTCOMES[action]
    outcome = random.choices(base["outcomes"], weights=base["probs"], k=1)[0]
    npc.adjust_state(outcome)

    # Possible secondary effect
    if outcome in SECONDARY_OUTCOMES:
        sec = SECONDARY_OUTCOMES[outcome]
        sub_outcome = random.choices(sec["outcomes"], weights=sec["probs"], k=1)[0]
        npc.adjust_state(sub_outcome)
        outcome = f"{outcome} → {sub_outcome}"

    return outcome


# ============================================================
# LLM DECISIONS
# ============================================================
def get_human_input() -> str:
    """Get advice from human player."""
    print("\n>>> What advice do you give to the NPC? (or press Enter to skip)")
    advice = input("Your advice: ").strip()
    return advice if advice else None

def choose_action_llm(npc: NPC, human_advice: str = None) -> str:
    available_actions = ["Chat with Keeper", "Get Drunk"]
    if npc.mood > 50 and npc.health > 60:
        available_actions.append("Accept a Quest")

    action_list = ", ".join(available_actions)
    
    advice_section = ""
    if human_advice:
        advice_section = f"""
A traveler urgently advises you: "{human_advice}"

This advice seems important. You should consider it and explain your reasoning for following or ignoring it.
"""

    prompt = f"""
You are roleplaying {npc.name}, a {', '.join(npc.traits)} adventurer in a medieval tavern.

Your current state:
Health={npc.health}, Money={npc.money}, Mood={npc.mood}
{advice_section}

Available actions: {action_list}

Decision rules:
- If health is low (<40), avoid dangerous activities
- If money is low (<50), prioritize earning gold
- If mood is low (<40), seek mood-boosting activities
- You are curious and impulsive, so you take risks
- If someone gives you urgent advice, take it seriously (though you may still disagree)

Think step-by-step:
1. What is the traveler's advice about?
2. Does it make sense given your situation?
3. What action best addresses this concern?

Respond in this format:
REASONING: [ONE sentence about the advice and your decision]
ACTION: [one of: {action_list}]
"""

    response = ollama_chat(prompt, temperature=0.5)
    
    # Extract and display reasoning compactly
    if "REASONING:" in response:
        reasoning_line = response.split("REASONING:")[1].split("ACTION:")[0].strip()
        print(f"{reasoning_line}")
    
    # Parse the action
    for act in available_actions:
        if f"ACTION: {act}" in response or act.lower() in response.lower().split("action:")[-1]:
            return act

    return "Chat with Keeper"


def describe_day_llm(npc: NPC, action: str, event: str) -> str:
    prompt = f"""
Write a short (2-3 sentence) medieval-style journal entry describing the day of {npc.name}.
Today's action: {action}.
Outcome: {event}.
NPC State at end: Health={npc.health}, Money={npc.money}, Mood={npc.mood}.
Keep it immersive and in-character.
"""
    return ollama_chat(prompt)


def adjust_mood_llm(npc: NPC) -> None:
    """Ask LLM how mood should change based on previous day."""
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


# ============================================================
# MAIN SIMULATION LOOP
# ============================================================
def run_simulation(days: int = 10):
    npc = NPC()
    print(f"=== Beginning Simulation with {npc.name} ===")

    for day in range(1, days + 1):
        print(f"\n--- DAY {day} ---")
        print(f"Current State: Health={npc.health}, Money={npc.money}, Mood={npc.mood}")

        adjust_mood_llm(npc)
        if not npc.alive():
            print("NPC has died. Simulation ends.")
            break

        # Get human advice
        human_advice = "" if day == 1 else get_human_input()

        action = choose_action_llm(npc, human_advice)
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
            "human_advice": human_advice,
            "state": npc.state()
        })

        if npc.won():
            print(f"{npc.name} has achieved wealth and wins the game!")
            break
        if not npc.alive():
            print(f"{npc.name} has died. Final State: {npc.state()}")
            break

        time.sleep(1)

    print("\n=== End of Simulation ===")
    print(json.dumps(npc.decision_log, indent=2))


if __name__ == "__main__":
    run_simulation(10)
