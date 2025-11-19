import json
import time
from npc import NPC
from actions import perform_action
from llm_decisions import (
    get_human_input,
    choose_action_llm,
    describe_day_llm,
    adjust_mood_llm,
    reflect_llm
)


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

        if day % 3 == 0:
            reflect_llm(npc)

        time.sleep(1)

    print("\n=== End of Simulation ===")
    print(json.dumps(npc.decision_log, indent=2))

