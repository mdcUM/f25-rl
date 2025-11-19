import random
from typing import TYPE_CHECKING
from config import ACTION_OUTCOMES, SECONDARY_OUTCOMES

if TYPE_CHECKING:
    from npc import NPC


# ============================================================
# ACTION LOGIC
# ============================================================
def perform_action(npc: "NPC", action: str) -> str:
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

    npc.memory.remember(action, outcome)
    npc.short_term_memory.add(f"{action} → {outcome}")
    npc.memory.short_term = npc.short_term_memory  # keep CharacterMemory in sync
    npc.memory.save()

    return outcome

