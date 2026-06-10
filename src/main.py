
# Main to start simulation
# We want to simulate a masspanic in an arena
# Due to the limited computing power we simulate with a few agents f.e. 4000 but count one agent as f.e. 10 persons.
from environment import EnvironmentConfig
from model import PanicSimModel
from pathlib import Path
import matplotlib.pyplot as plt

def print_simulation_summary(model: PanicSimModel,real_people,people_per_agent) -> None:
    model_data = model.datacollector.get_model_vars_dataframe()
    active_steps = model_data[model_data["active_agents"] > 0]

    print("\n--- Simulation Summary ---")
    print(f"Number of real_people:{real_people}")
    print(f"Number of people_per_agent:{people_per_agent}")
    print(f"Total agents: {model.num_agents}")
    print(f"Evacuated agents: {model.evacuated_agents}")
    print(f"Dead agents: {model.dead_agents}")
    print(f"Steps: {model.steps}")
    print(f"Fire cells: {int(model.fire_grid.sum())}")

    print("\n--- Rates ---")
    print(f"Evacuation rate: {model.evacuated_agents / model.num_agents:.3f}")
    print(f"Death rate: {model.dead_agents / model.num_agents:.3f}")

    print("\n--- Panic ---")
    print(f"Final active average panic: {active_steps['average_panic'].iloc[-1]:.3f}")
    print(f"Mean average panic: {active_steps['average_panic'].mean():.3f}")
    print(f"Max average panic: {active_steps['average_panic'].max():.3f}")

    print("\n--- Last steps ---")
    print(model_data.tail())

def create_environment_config(**changes):
    return EnvironmentConfig(
            exit_width=changes.get("exit_width", 2),
            use_stage=changes.get("use_stage", True),
            use_barriers=changes.get("use_barriers", True),

            max_agents_per_cell=changes.get("max_agents_per_cell", 4),
            border_spawn_protection=changes.get("border_spawn_protection", 2),
            random_seed=changes.get("random_seed", 42),
            fire_start_step=changes.get("fire_start_step", 10),
            fire_start_size=changes.get("fire_start_size", 5),
            fire_spread_interval=changes.get("fire_spread_interval", 2),
            fire_spread_size=changes.get("fire_spread_size", 10),

            blocked_panic_increase=changes.get("blocked_panic_increase", 0.1),
            panic_decay=changes.get("panic_decay", 0.04),
            panic_from_other_cell_increase_value=changes.get("panic_from_other_cell_increase_value", 0.08),
            fire_near_panic_increase=changes.get("fire_near_panic_increase", 0.2)
    )

def run_scenario_comparison(num_agents):
    scenarios = [
        ("Baseline", {}),
        ("No stage / no barriers", {"use_stage": False, "use_barriers": False}),
        ("Wider exits", {"exit_width": 8}),
        ("Slower fire", {"fire_spread_interval": 5, "fire_spread_size": 5}),
        ("Faster fire", {"fire_spread_interval": 1, "fire_spread_size": 27}),
    ]

    results = []

    print("\n--- Scenario Comparison Table ---")
    print("Scenario | Evacuated | Dead | Steps | Fire cells | Evacuation rate | Death rate | Mean panic | Max panic")
    print("-" * 113)

    for name, changes in scenarios:
        model = PanicSimModel(create_environment_config(**changes), num_agents)
        model.run_model()

        model_data = model.datacollector.get_model_vars_dataframe()
        active_steps = model_data[model_data["active_agents"] > 0]
        row = {
            "Scenario": name,
            "Evacuated": model.evacuated_agents,
            "Dead": model.dead_agents,
            "Steps": model.steps,
            "Fire cells": int(model.fire_grid.sum()),
            "Evacuation rate": model.evacuated_agents / model.num_agents,
            "Death rate": model.dead_agents / model.num_agents,
            "Mean panic": active_steps["average_panic"].mean(),
            "Max panic": active_steps["average_panic"].max(),
        }
        results.append(row)

        print(
            f"{row['Scenario']} | "
            f"{row['Evacuated']} | "
            f"{row['Dead']} | "
            f"{row['Steps']} | "
            f"{row['Fire cells']} | "
            f"{row['Evacuation rate']:.4f} | "
            f"{row['Death rate']:.4f} | "
            f"{row['Mean panic']:.4f} | "
            f"{row['Max panic']:.4f}"
        )

    

    names = [row["Scenario"] for row in results]
    death_rates = [row["Death rate"] * 100 for row in results]
    steps = [row["Steps"] for row in results]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].bar(names, death_rates)
    axes[0].set_title("Death rate by scenario")
    axes[0].set_ylabel("Death rate (%)")
    axes[0].tick_params(axis="x", rotation=25)

    axes[1].bar(names, steps)
    axes[1].set_title("Steps to absorption by scenario")
    axes[1].set_ylabel("Simulation steps")
    axes[1].tick_params(axis="x", rotation=25)

    fig.suptitle("Scenario comparison, seed 42")
    fig.tight_layout()

    output = Path("plots") / "scenario_comparison.png"
    output.parent.mkdir(exist_ok=True)
    fig.savefig(output, dpi=200)
    print(f"\nSaved figure: {output}")
    
def main():
    real_people = 40000
    people_per_agent = 10

    num_agents = real_people//people_per_agent

    env_config = EnvironmentConfig(
            exit_width=2,
            use_stage=True,
            use_barriers=True,

            max_agents_per_cell = 4,
            border_spawn_protection = 2,
            random_seed=42,
            fire_start_step = 10,
            #max 5
            fire_start_size = 5,
            fire_spread_interval = 2, # fire expands all x steps
            fire_spread_size = 10, #how many cells a fire cell will ignite


            #panic values from 0 to 1
            blocked_panic_increase = 0.1,  #how much the panic increases whe blocked (no moves)
            panic_decay = 0.04, #decay if a move is available
            panic_from_other_cell_increase_value = 0.08, # % of the median panic from the next cell the agent add
            fire_near_panic_increase = 0.2 #if a fire is near the panic of the agent increases
    )

    model= PanicSimModel(env_config, num_agents)
    model.run_model()
    print_simulation_summary(model,real_people,people_per_agent)
    run_scenario_comparison(num_agents)

if __name__ == "__main__":
    main()
