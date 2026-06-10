#https://mesa.readthedocs.io/latest/apis/visualization.html#../tutorials/6_visualization_custom

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import solara

from mesa.visualization import SolaraViz, make_plot_component
from mesa.visualization.utils import update_counter

from environment import EnvironmentConfig, CellType
from model import PanicSimModel


def get_agent_color(agent):
    if agent.panic_level < 0.33:
        return "green"

    if agent.panic_level < 0.66:
        return "orange"

    return "red"


@solara.component
def ArenaView(model):
    # updates the map so
    update_counter.get()

    fig, ax = plt.subplots(figsize=(9, 7))

    # Same order as the CellType enum.
    environment_cmap = ListedColormap([
        "white",        # FREE
        "dimgray",      # STAGE
        "black",        # OBSTACLE
        "deepskyblue",  # EXIT
    ])

    ax.imshow(
        model.environment_grid.T,
        origin="lower",
        cmap=environment_cmap,
        vmin=CellType.FREE,
        vmax=CellType.EXIT,
        alpha=0.85,
    )

    # Only draw cells where there actually is fire.
    fire_layer = np.ma.masked_where(
        model.fire_grid.T == 0,
        model.fire_grid.T,
    )

    ax.imshow(
        fire_layer,
        origin="lower",
        cmap=ListedColormap(["red"]),
        alpha=0.75,
    )

    agent_x = []
    agent_y = []
    agent_colors = []
    active_count = 0

    for agent in model.agents:
        if agent.cell is None:
            continue

        if hasattr(agent, "active") and not agent.active:
            continue

        x, y = agent.cell.coordinate

        agent_x.append(x)
        agent_y.append(y)
        agent_colors.append(get_agent_color(agent))
        active_count += 1

    ax.scatter(
        agent_x,
        agent_y,
        c=agent_colors,
        s=8,
        alpha=0.9,
    )

    ax.set_xlim(-1, model.environment_config.width)
    ax.set_ylim(-1, model.environment_config.height)
    ax.set_aspect("equal")

    ax.set_title(
        f"Step {model.steps} | "
        f"Active: {active_count} | "
        f"Evacuated: {model.evacuated_agents} | "
        f"Dead: {model.dead_agents}"
    )

    ax.set_xlabel("x")
    ax.set_ylabel("y")

    solara.FigureMatplotlib(fig)
    plt.close(fig)


env_config = EnvironmentConfig(
    exit_width=2,
    use_stage=True,
    use_barriers=True,
    max_agents_per_cell=4,
    border_spawn_protection=2,
    random_seed=42,

    fire_start_step=10,
    fire_start_size=5,
    fire_spread_interval=2,
    fire_spread_size=10,

    blocked_panic_increase=0.1,
    panic_decay=0.04,
    panic_from_other_cell_increase_value=0.08,
    fire_near_panic_increase=0.2,
)


model_params = {
    "environment_config": env_config,
    "num_agents": 4000,
}


model = PanicSimModel(**model_params)

panic_plot = make_plot_component("average_panic")

agent_plot = make_plot_component([
    "active_agents",
    "evacuated_agents",
    "dead_agents",
])

fire_plot = make_plot_component("fire_cells")


page = SolaraViz(
    model,
    model_params=model_params,
    components=[
        ArenaView,
        panic_plot,
        agent_plot,
        fire_plot,
    ],
    name="Mass Panic Simulation",
)
