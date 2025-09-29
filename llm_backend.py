"""
Simple FastAPI backend to interface with Gemma via Ollama
Decides character actions from LLM reasoning
"""

from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import json

app = FastAPI()

class CharacterState(BaseModel):
    name: str
    health: int
    greed: int
    fatigue: int
    risk_aversion: int
    goals: list

@app.post("/decide")
def get_decision(state: CharacterState):
    # Build the prompt
    prompt = f"""
    You are simulating a fantasy character making decisions.
    State:
    - Name: {state.name}
    - Health: {state.health}
    - Greed: {state.greed}
    - Fatigue: {state.fatigue}
    - Risk Aversion: {state.risk_aversion}
    - Goals: {state.goals}

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

    # Run Ollama locally
    result = subprocess.run(
        ["ollama", "run", "gemma:2b", "--json"],
        input=prompt.encode("utf-8"),
        capture_output=True
    )

    # Ollama streams JSON lines → take last line
    output_lines = result.stdout.decode().strip().split("\n")
    last_line = output_lines[-1]
    try:
        parsed = json.loads(last_line)["response"]
        return json.loads(parsed)  # return parsed decision
    except Exception as e:
        return {"error": str(e), "raw_output": last_line}
