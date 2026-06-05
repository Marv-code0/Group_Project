print("hello")
# Main to start simulation
# We want to simulate a masspanic in an arena
# Due to the limited computing power we simulate with a few agents f.e. 4000 but count one agent as f.e. 20 persons.
from environment import EnvironmentConfig

def main():
    real_people = 40000
    people_per_agent = 20

    num_agents = real_people//people_per_agent

    env_config = EnvironmentConfig(
            exit_width=8,
            use_stage=True,
            use_barriers=True,

            max_agents_per_cell = 4,
            border_spawn_protection = 2,
            random_seed=42
    )

