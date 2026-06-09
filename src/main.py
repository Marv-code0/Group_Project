
# Main to start simulation
# We want to simulate a masspanic in an arena
# Due to the limited computing power we simulate with a few agents f.e. 4000 but count one agent as f.e. 10 persons.
from environment import EnvironmentConfig
from model import PanicSimModel

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

if __name__ == "__main__":
    main()
