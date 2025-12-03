"""
Main entry point for the game simulation.
This module imports and runs the simulation from the modular components.
"""
from simulation import run_simulation


if __name__ == "__main__":
    run_simulation(10)
    print("\n=== End of Program ===")