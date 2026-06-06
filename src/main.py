
# Main to start simulation
# We want to simulate a masspanic in an arena
# Due to the limited computing power we simulate with a few agents f.e. 4000 but count one agent as f.e. 20 persons.
from environment import EnvironmentConfig
from model import PanicSimModel

def main():
    real_people = 40000
    people_per_agent = 20

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
    )

    model= PanicSimModel(env_config, num_agents)
    model.run_model()

    model_data = model.datacollector.get_model_vars_dataframe()
    print(model_data.tail())
    print("Evacuated:", model.evacuated_agents)
    print("Dead:", model.dead_agents)
    print("Steps:", model.steps)
    print("Fire cells:", int(model.fire_grid.sum()))
    print("Evacuation rate:", model.evacuated_agents / model.num_agents)
    print("Death rate:", model.dead_agents / model.num_agents)
    print("Average panic:", model_data["average_panic"].iloc[-1])
    print("Max average panic:", model_data["average_panic"].max())

    active_steps = model_data[model_data["active_agents"] > 0]

    print("Final active average panic:", round(active_steps["average_panic"].iloc[-1], 3))
    print("Mean average panic:", round(active_steps["average_panic"].mean(), 3))
    print("Max average panic:", round(active_steps["average_panic"].max(), 3))
if __name__ == "__main__":
    main()