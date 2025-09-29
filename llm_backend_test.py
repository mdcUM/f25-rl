"""
Test script to test Gemma/Ollama/JSON integration.
"""

import subprocess
import json

# Define a sample character state
state = {
    "name": "Grindle",
    "health": 70,
    "greed": 8,
    "fatigue": 3,
    "risk_aversion": 5,
    "goals": ["Corner the Market on Weasel Pelts"]
}

prompt = f"""
You are simulating a fantasy character making decisions.
State:
- Name: {state['name']}
- Health: {state['health']}
- Greed: {state['greed']}
- Fatigue: {state['fatigue']}
- Risk Aversion: {state['risk_aversion']}
- Goals: {state['goals']}

Available actions:
- Adventure in Forest
- Rob Merchant
- Scout Town

Respond ONLY in valid JSON with this schema:
{{
  "chosen_action": "...",
  "reasoning": "...",
  "expected_outcome": "...",
  "risk_level": "low/medium/high",
  "reward_estimate": 0
}}
"""

# Run Ollama with Gemma2B
result = subprocess.run(
    ["ollama", "run", "gemma:2b"],
    input=prompt.encode("utf-8"),
    capture_output=True
)

# Decode output
output = result.stdout.decode().strip()

print("Raw output:\n", output)

# Try parsing as JSON (if the model followed instructions)
try:
    parsed = json.loads(output)
    print("\nParsed decision:")
    print(parsed)
except Exception:
    print("\nCould not parse as JSON. Model returned free text instead.")
