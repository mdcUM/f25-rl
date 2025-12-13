import json
import re
from typing import TYPE_CHECKING
from llm_interface import ollama_chat
from config import WORLD_CONTEXT

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
    
    # Quest availability
    if npc.mood > 50 and npc.health > 60:
        available_actions.append("Accept a Quest")
    
    # Marketplace and Woods always available
    available_actions.extend(["Visit the Marketplace", "Explore the Woods"])
    
    action_list = ", ".join(available_actions)

    previous_context = (
        f"Yesterday: {npc.last_report}"
        if npc.last_report != "Woke up in the tavern."
        else ""
    )

    # Calculate current state descriptors
    health_status = "HEALTHY" if npc.health > 60 else "INJURED" if npc.health > 40 else "CRITICAL"
    money_status = "WEALTHY" if npc.money > 100 else "COMFORTABLE" if npc.money > 50 else "BROKE"
    mood_status = "CONTENT" if npc.mood > 60 else "NEUTRAL" if npc.mood > 40 else "MISERABLE"

    # -------- ADVICE SECTION ----------
    advice_section = ""
    if human_advice:
        npc.trust = min(100, npc.trust + 15)

        trust_tier = (
            "You barely know this person and may ignore their advice."
            if npc.trust < 30 else
            "You somewhat trust this person. Consider their advice carefully."
            if npc.trust < 70 else
            "You deeply trust this person. Their advice should heavily influence your decision."
        )

        advice_section = f"""
=== ADVICE FROM YOUR COMPANION ===
"{human_advice}"
Trust Level: {npc.trust:.1f}/100 — {trust_tier}

If trust >= 30: Their advice should be your PRIMARY consideration.
"""

    # Get history
    history = npc.memory.summarize()

    # Helper to safely format goals that may be a list of strings or dicts
    def _format_goals(goals) -> str:
        try:
            if isinstance(goals, list):
                parts = []
                for g in goals:
                    if isinstance(g, dict):
                        parts.append(
                            g.get("name")
                            or g.get("goal")
                            or json.dumps(g)
                        )
                    else:
                        parts.append(str(g))
                return ", ".join(parts)
            return str(goals)
        except Exception:
            return str(goals)

    # ---------- ENHANCED STORY PROMPT ----------
    prompt = f"""You are {npc.name}, a {', '.join(npc.traits)} adventurer in the kingdom of Valdoria.

{WORLD_CONTEXT}

=== YOUR CURRENT SITUATION (Day {len(npc.decision_log) + 1}) ===
Health: {npc.health:.1f} / 100 ({health_status})
Money: {npc.money:.1f} gold ({money_status})
Mood: {npc.mood:.1f} / 100 ({mood_status})

{previous_context}

=== YOUR RECENT ADVENTURES ===
{history}

Your Goals: {_format_goals(npc.memory.goals)}

{advice_section}

=== AVAILABLE ACTIONS ===
{action_list}

=== DECISION GUIDANCE ===
Consider your circumstances carefully:
- If your companion gave advice AND trust >= 30: Their counsel should guide you
- If health < 40: Prioritize survival (avoid dangerous quests)
- If money < 20: You desperately need income
- If mood < 40: Seek joy or purpose to maintain your spirit
- Review your recent adventures - what patterns emerge? What worked? What failed?

The kingdom's fate may hinge on your choices. Choose wisely.

Respond in this format:
REASONING: [One sentence reflecting on your situation]
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


def describe_day_llm(npc: "NPC", action: str, event: str) -> str:
    """Generate consistent journal entries."""
    
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
- Reference the actual outcome (don't invent stats)
- Show emotional state through word choice
- Connect to previous entry if relevant

Write ONLY the journal entry. Do not include notes, explanations, or meta-commentary.

Example format: "Today I [action]. [Outcome and reaction]. [Brief reflection on state/feelings]."
"""
    
    report = ollama_chat(prompt, temperature=0.6)
    
    # Strip out any meta-commentary in parentheses or after "Note:"
    if "(Note:" in report:
        report = report.split("(Note:")[0].strip()
    if "(I tried" in report:
        report = report.split("(I tried")[0].strip()
    
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
            reflection_text = data.get('reflection', 'I pondered my journey')
            npc.memory.remember("Reflection", reflection_text)
            
            npc.memory.save()
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

