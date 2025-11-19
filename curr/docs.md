# Game Simulation Documentation

This document explains the structure and functionality of each module in the game simulation system.

## Table of Contents

- [config.py](#configpy)
- [memory.py](#memorypy)
- [npc.py](#npcpy)
- [llm_interface.py](#llm_interfacepy)
- [actions.py](#actionspy)
- [llm_decisions.py](#llm_decisionspy)
- [simulation.py](#simulationpy)
- [main.py](#mainpy)

---

## config.py

**Purpose**: Contains all game configuration constants including available actions and their probabilistic outcomes.

### Constants

#### `ACTIONS`
- **Type**: `List[str]`
- **Description**: List of all available actions the NPC can take in the game.
- **Values**: `["Chat with Keeper", "Accept a Quest", "Get Drunk"]`

#### `ACTION_OUTCOMES`
- **Type**: `Dict[str, Dict[str, List]]`
- **Description**: Defines the primary outcomes for each action with their probabilities. Each action maps to a dictionary containing:
  - `"outcomes"`: List of possible outcome strings
  - `"probs"`: List of probabilities (must sum to 1.0) corresponding to each outcome
- **Actions**:
  - `"Chat with Keeper"`: Can result in encouragement (+10 mood), discouragement (-10 mood), receiving a gift, or fighting
  - `"Accept a Quest"`: Can result in fighting a dragon, defending a caravan, or cleaning a statue
  - `"Get Drunk"`: Can result in losing money, losing health, or gaining mood

#### `SECONDARY_OUTCOMES`
- **Type**: `Dict[str, Dict[str, List]]`
- **Description**: Defines secondary outcomes that can occur after certain primary outcomes. Used for chained events (e.g., if you receive a gift, you might get money or a health potion).
- **Structure**: Same as `ACTION_OUTCOMES`, but triggered conditionally based on primary outcomes.

---

## memory.py

**Purpose**: Implements the memory system for NPCs, handling both persistent long-term memory and short-term event tracking.

### Classes

#### `CharacterMemory`

**Purpose**: Manages persistent character memory that is saved to and loaded from JSON files.

##### `__init__(self, name: str, file_path: str)`
- **Parameters**:
  - `name`: The character's name
  - `file_path`: Path to the JSON file where memory is stored
- **Description**: Initializes the memory system. If the file exists, loads existing data; otherwise creates default memory structure with traits, goals, and empty memory arrays.

##### `remember(self, action: str, outcome: str)`
- **Parameters**:
  - `action`: The action that was taken
  - `outcome`: The outcome of that action
- **Description**: Adds a new memory entry in the format "action → outcome". Maintains only the last 5 memories (FIFO queue). Automatically saves to file after adding.

##### `summarize(self) -> str`
- **Returns**: A string representation of the last 5 memories, joined with " → "
- **Description**: Returns a human-readable summary of recent memories. Returns "No memories yet." if memory is empty.

##### `save(self)`
- **Description**: Saves the current memory state (traits, goals, memory entries, and short-term memory) to the JSON file specified in `__init__`.

---

#### `ShortTermMemory`

**Purpose**: Manages a rolling buffer of recent events for immediate context.

##### `__init__(self, max_size=5)`
- **Parameters**:
  - `max_size`: Maximum number of events to keep (default: 5)
- **Description**: Initializes an empty short-term memory buffer.

##### `add(self, event: str)`
- **Parameters**:
  - `event`: String description of the event to add
- **Description**: Adds a new event to the recent events list. If the list exceeds `max_size`, removes the oldest event (FIFO).

##### `to_dict(self)`
- **Returns**: Dictionary representation of the short-term memory
- **Description**: Serializes the short-term memory to a dictionary for JSON storage.

##### `from_dict(data)`
- **Parameters**:
  - `data`: Dictionary containing serialized short-term memory
- **Returns**: A new `ShortTermMemory` instance
- **Description**: Static method that creates a `ShortTermMemory` object from a dictionary (used when loading from JSON).

---

## npc.py

**Purpose**: Defines the NPC (Non-Player Character) class that represents the game's main character with state, memory, and decision-making capabilities.

### Class

#### `NPC`

**Purpose**: Represents the main character in the simulation with attributes like health, money, mood, and memory.

##### `__init__(self, name="Aldric", traits=["curious"], health=100.0, money=20.0, mood=50.0)`
- **Parameters**:
  - `name`: Character name (default: "Aldric")
  - `traits`: List of character traits (default: ["curious"])
  - `health`: Starting health value (default: 100.0)
  - `money`: Starting money value (default: 20.0)
  - `mood`: Starting mood value (default: 50.0)
- **Description**: Initializes a new NPC with default or specified attributes. Creates a `CharacterMemory` instance and links it to short-term memory. Initializes an empty decision log.

##### `state(self) -> Dict[str, Any]`
- **Returns**: Dictionary containing current NPC state (name, traits, health, money, mood)
- **Description**: Returns a snapshot of the NPC's current state for logging and display purposes.

##### `adjust_state(self, effect: str)`
- **Parameters**:
  - `effect`: String describing the state change (e.g., "+10 mood", "-20 health")
- **Description**: Parses effect strings and updates NPC attributes accordingly. Handles:
  - Mood changes: `+10 mood`, `-10 mood`, `+20 mood` (clamped to 0-100)
  - Health changes: `+10 health`, `-10 health`, `-20 health`, `-30 health`, `Lose 0.2 health`, `Die` (clamped to 0-100, except "Die" sets to 0)
  - Money changes: `+10 money`, `+20 money`, `+50 money`, `Lose 0.5 money` (money can go below 0, but clamped to 0 minimum)

##### `alive(self) -> bool`
- **Returns**: `True` if health > 0, `False` otherwise
- **Description**: Checks if the NPC is still alive.

##### `won(self) -> bool`
- **Returns**: `True` if money >= 150, `False` otherwise
- **Description**: Checks if the NPC has achieved the victory condition (accumulated enough wealth).

---

## llm_interface.py

**Purpose**: Provides a simple interface for communicating with the Ollama LLM (Large Language Model) API.

### Functions

#### `ollama_chat(prompt: str, model="llama3.1", temperature: float = 0.9) -> str`
- **Parameters**:
  - `prompt`: The text prompt to send to the LLM
  - `model`: The model name to use (default: "llama3.1")
  - `temperature`: Controls randomness in responses (0.0 = deterministic, 1.0 = very random, default: 0.9)
- **Returns**: The LLM's response as a stripped string
- **Description**: Sends a prompt to the Ollama chat API and returns the response. If an error occurs, prints the error and returns "Get Drunk" as a fallback action.

---

## actions.py

**Purpose**: Handles the execution of game actions and their probabilistic outcomes.

### Functions

#### `perform_action(npc: "NPC", action: str) -> str`
- **Parameters**:
  - `npc`: The NPC instance performing the action
  - `action`: The action string (must be in `ACTIONS` from config)
- **Returns**: String describing the outcome(s) of the action
- **Description**: 
  1. Looks up the action in `ACTION_OUTCOMES` from config
  2. Randomly selects an outcome based on the probability weights
  3. Applies the outcome's effects to the NPC using `npc.adjust_state()`
  4. Checks if the outcome triggers a secondary outcome (from `SECONDARY_OUTCOMES`)
  5. If so, randomly selects and applies a secondary outcome
  6. Records the action and outcome in the NPC's memory
  7. Saves the memory to disk
  8. Returns a string describing the outcome (may include chained outcomes like "Fight a Dragon → Slay the dragon +50 money")

---

## llm_decisions.py

**Purpose**: Contains all functions that use the LLM to make decisions, generate descriptions, and handle NPC reasoning.

### Functions

#### `get_human_input() -> str`
- **Returns**: The user's input string, or `None` if empty
- **Description**: Prompts the user for advice to give to the NPC. Returns `None` if the user just presses Enter (skips advice).

#### `choose_action_llm(npc: "NPC", human_advice: str = None) -> str`
- **Parameters**:
  - `npc`: The NPC making the decision
  - `human_advice`: Optional advice string from the human player
- **Returns**: The chosen action string
- **Description**: 
  1. Determines available actions based on NPC state (quests only available if mood > 50 and health > 60)
  2. Constructs a detailed prompt including NPC state, memories, goals, and optional human advice
  3. Sends prompt to LLM asking for reasoning and action choice
  4. Extracts and displays the reasoning from the LLM response
  5. Parses the response to find the chosen action
  6. Returns the action (defaults to "Chat with Keeper" if parsing fails)

#### `describe_day_llm(npc: "NPC", action: str, event: str) -> str`
- **Parameters**:
  - `npc`: The NPC whose day is being described
  - `action`: The action taken during the day
  - `event`: The outcome of that action
- **Returns**: A narrative description of the day
- **Description**: 
  1. Constructs a prompt asking the LLM to write a 2-3 sentence medieval-style journal entry
  2. Includes context about the action, outcome, memories, and current state
  3. Sends prompt to LLM
  4. Stores the report in `npc.last_report`
  5. Returns the generated narrative

#### `adjust_mood_llm(npc: "NPC") -> None`
- **Parameters**:
  - `npc`: The NPC whose mood should be adjusted
- **Description**: 
  1. Constructs a prompt asking the LLM to determine mood adjustment (-10 to +10) based on the previous day's report
  2. Sends prompt to LLM
  3. Extracts an integer from the response using regex
  4. Updates NPC mood (clamped to 0-100)
  5. Silently fails if parsing fails (no mood change)

#### `reflect_llm(npc: "NPC") -> None`
- **Parameters**:
  - `npc`: The NPC reflecting on their experiences
- **Description**: 
  1. Constructs a prompt asking the NPC to reflect on recent memories and suggest goal/mindset adjustments
  2. Asks for JSON response with goals and reflection text
  3. Sends prompt to LLM
  4. Extracts JSON from response using regex
  5. Parses JSON and updates NPC goals if valid
  6. Records the reflection in memory
  7. Saves memory to disk
  8. Silently fails if JSON parsing fails

---

## simulation.py

**Purpose**: Contains the main game loop that orchestrates the simulation.

### Functions

#### `run_simulation(days: int = 10) -> None`
- **Parameters**:
  - `days`: Number of days to simulate (default: 10)
- **Description**: Main simulation loop that:
  1. Creates a new NPC instance
  2. For each day:
     - Displays current day and NPC state
     - Adjusts mood based on previous day (via LLM)
     - Checks if NPC is alive (ends if dead)
     - Gets human advice (skips on day 1)
     - Chooses an action using LLM
     - Performs the action and gets outcome
     - Generates a narrative report of the day
     - Logs the day's decision
     - Checks win condition (money >= 150)
     - Checks death condition again
     - Every 3 days, triggers reflection
     - Waits 1 second between days
  3. At the end, prints the complete decision log as JSON

---

## main.py

**Purpose**: Simple entry point for running the simulation.

### Code

#### `if __name__ == "__main__":`
- **Description**: When the script is run directly (not imported), it calls `run_simulation(10)` to start a 10-day simulation.

---

## Module Dependencies

```
main.py
  └── simulation.py
        ├── npc.py
        │     └── memory.py
        ├── actions.py
        │     ├── config.py
        │     └── npc.py (type hint only)
        └── llm_decisions.py
              ├── llm_interface.py
              └── npc.py (type hint only)
```