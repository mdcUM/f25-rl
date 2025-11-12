import json, random, re, os
import ollama
from typing import Dict, List, Any

# ============================================================
# OVERVIEW / GAME LOOP
# ============================================================

    # Start with one NPC and one location with defined actions and probabilities before "letting him loose". LLM will determine actions and description output. 

    # TIMELINE (Per Day of 10 days)
    # 1) Wake up with report of mood (determined by LLM based on prev. EOD report).
    # 2) Perform 1 action --> report description --> report outcomes (determined by hardcoded probabilities) and physical state changes (determined by outcomes)
    # 3) EOD Report from LLM includes description of event for the day, + recap of NPC State.
    # 4) Sleep --> Next Day --> Apply world updates if needed (like famine)

    # NOTE:
    # The result of each action is probabilistic. Outcomes reported after each action, EOD summary reported after 1 action.

# ============================================================
# NPC State
# ============================================================

    # Hardcoded: Traits: {"curious"}

    # Physical state: Health (?/100), Money

    # Mental state: Mood (?/100) -- adjusted by LLM by increment of +-(0 to 10). LLM determines by evaluating Phsyical state + last EOD report

    # NOTE: Death occurs at 0 health, End of Game report displays last NPC State + cause of death
    # NOTE: WIN occurs at 150 money. End of Game report displays last NPC State.

# ============================================================
# Environment -- Tavern only so far
# ============================================================

    # Tavern

    # PRIMARY ACTIONS: {"Chat with the Keeper", "Accept a quest", "Get Drunk"}
    # NOTE: Repeat actions allowed, actions selected by LLM based on Mental state

# ============================================================
# Primary Action Outcomes and Probabilities
# ============================================================

    # 1) Chat with the Keeper:
        # OUTCOMES: {"Keeper encourages you (+10/100 mood)", 
        #           "Keeper discourages you (-10/100 mood)", 
        #           "Receive a gift from Keeper", "Fight the Keeper"}
        # PROBABILITIES: (0.5, 0.15, 0.3, 0.05)

    # 2) Accept a Quest:
        # OUTCOMES: {"Fight a Dragon", "Defend a caravan", "Clean the hero statue"}
        # PROBABILITIES: (0.1, 0.7, 0.2)

    # 3) Get Drunk:
        # OUTCOMES: {"Lose 0.5(money)", "Lose .2(health)", "Gain +20 mood"}
        # PROBABILITIES: (0.4, 0.4, 0.2)

    # NOTE: Accepting a quest is only an available action if: mood >= 50 && health >= 60.
     
# ============================================================
# Secondary Action Outcomes and Probabilities
# ============================================================

# From Chat with the Keeper:

    # 1) Gift from Keeeper:
        # OUTCOMES: {"+20 money", "Health potion +10 health"}
        # PROBABILITIES: (0.5, 0.5)

    # 2) Fight the Keeper:
        # OUTCOMES {"+10 money", "Nothing happens", "-20 health"}
        # PROBABILITIES: (0.1, 0.3, 0.6)

# From Accept a Quest:

    # 1) Fight a Dragon:
        # OUTCOMES: {"Slay the dragon + 50 money", "Die - 1(health)", "Retreat -0.3(health)"}
        # PROBABILITIES (0.5, 0.1, 0.4)

    # 2) Defend a Caravan:
        # OUTCOMES: {"Protect the caravan + 20 money", "Abandon caravan after ambush -0.1(health)"}
        # PROBABILITIES: (0.5, 0.5)

    # 3) Clean Hero Statue:
        # OUTCOMES: {"Cleaned + 10 money", "Blessed by the statue +10 health"}
        # PROBABILITIES: (0.9, 0.1)






# ============================================================
# World State
# ============================================================

    # TBD, but maybe after 20 days a famine occurs, reducing money from quests by 20%.



