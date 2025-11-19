import json
import re
from typing import TYPE_CHECKING
from llm_interface import ollama_chat

if TYPE_CHECKING:
    from npc import NPC


# ============================================================
# LLM DECISIONS
# ============================================================
def get_human_input() -> str:
    """Get advice from human player."""
    print("\n>>> What advice do you give to the NPC? (or press Enter to skip)")
    advice = input("Your advice: ").strip()
    return advice if advice else None


def choose_action_llm(npc: "NPC", human_advice: str = None) -> str:
    available_actions = ["Chat with Keeper", "Get Drunk"]
    if npc.mood > 50 and npc.health > 60:
        available_actions.append("Accept a Quest")

    action_list = ", ".join(available_actions)

    previous_context = (
        f"Yesterday's journal: {npc.last_report}"
        if npc.last_report != "Woke up in the tavern."
        else ""
    )

    # -------- ADVICE SECTION (only if there is advice) ----------
    advice_section = ""
    if human_advice:
        npc.trust = min(100, npc.trust + 5)

        trust_tier = (
            "You barely know this person and you're unsure whether to trust them."
            if npc.trust < 30 else
            "You somewhat trust this person and consider their intentions fair."
            if npc.trust < 70 else
            "You strongly trust this person and value their guidance."
        )

        advice_section = f"""
Someone offers you advice: "{human_advice}"
Trust Level: {npc.trust:.1f}/100 — {trust_tier}
Consider the advice only if it aligns with your needs.
"""

    # ---------- FINAL PROMPT ----------
    prompt = f"""You are {npc.name}, a {', '.join(npc.traits)} adventurer.

CURRENT STATE (Day {len(npc.decision_log) + 1}):
- Health: {npc.health:.1f}/100
- Money: {npc.money:.1f} gold
- Mood: {npc.mood:.1f}/100
- Trust Toward Advisor: {npc.trust:.1f}/100

{previous_context}

GOALS: {', '.join(npc.memory.goals)}
RECENT HISTORY: {npc.memory.summarize()}

{advice_section}

AVAILABLE ACTIONS: {action_list}

DECISION FRAMEWORK:
- Health < 40: Avoid danger, prioritize survival
- Money < 50: Seek profitable opportunities
- Mood < 40: Seek enjoyment to maintain morale
- Advice from humans is only considered when they speak AND trust is high

Think through:
1. What's my most pressing need right now?
2. Should advice matter today? (Only if present and trust justifies it.)
3. Which action best serves my priorities?

Respond EXACTLY like this:
REASONING: [One sentence]
ACTION: {available_actions[0]}
"""

    response = ollama_chat(prompt, temperature=0.7)

    # Extract reasoning
    if "REASONING:" in response:
        reasoning = response.split("REASONING:")[1].split("ACTION:")[0].strip()
        print(f"\n{npc.name}'s reasoning: {reasoning}")

    # Parse action
    for act in available_actions:
        if act in response:
            return act

    return available_actions[0]


# In llm_decisions.py - improve journal generation
def describe_day_llm(npc: "NPC", action: str, event: str) -> str:
    """Generate consistent journal entries."""
    
    # Establish a consistent date/era system
    day_number = len(npc.decision_log) + 1
    
    prompt = f"""Write a brief (2-3 sentence) journal entry for {npc.name}.

CONTEXT:
- Day {day_number} in the Year of the Golden Anvil
- Action taken: {action}
- What happened: {event}
- Current state: {npc.health:.0f} health, {npc.money:.0f} gold, feeling {"optimistic" if npc.mood > 60 else "troubled" if npc.mood < 40 else "steady"}

PREVIOUS ENTRY: {npc.last_report}

STYLE GUIDELINES:
- Write in first person as {npc.name}
- Maintain medieval/fantasy tone
- Reference the actual outcome (don't invent stats like "experience")
- Show emotional state through word choice
- Connect to previous entry if relevant

Example format: "Today I [action]. [Outcome and reaction]. [Brief reflection on state/feelings]."
"""
    
    report = ollama_chat(prompt, temperature=0.6)
    npc.last_report = report
    return report


def adjust_mood_llm(npc: "NPC") -> None:
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
    except (ValueError, IndexError):
        pass


def reflect_llm(npc: "NPC"):
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
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

