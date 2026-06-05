"""
Environment setup for the mass panic simulation.

The environment represents a simplified stadium / concert area:
- The grid is the stadium floor / field. rectangular
- People start inside the field area.
- Exits are specific cells at the grid border.
- Obstacles represent fences, barriers, stage areas or blocked zones.
"""

from dataclasses import dataclass
from enum import IntEnum
import numpy as np


EXIT_NUM = 6

class CellType(IntEnum):
    FREE = 0
    STAGE = 1
    OBSTACLE = 2
    EXIT = 3

@dataclass
class EnvironmentConfig:

    #variable
    exit_width: int
    use_stage: bool # if the stage in front is a blocked field
    use_barriers: bool # if there are f.e fences that an agent need to go around
    random_seed: int

    #crowd control
    max_agents_per_cell: int

    border_spawn_protection: int #how far from the borders an agent should spawn

    # fixed
    width: int = 100
    height: int = 80

#creates an environment grid for the model with the exits and the obsticales/stage grid[x,y] = 1 means this grid is type stage
def create_environment_grid(config: EnvironmentConfig) -> np.ndarray:
    grid = np.full(
        (config.width, config.height),
        CellType.FREE,
        dtype=np.int8
    )

    if config.use_stage:
        add_front_stage(grid, config)

    if config.use_barriers:
        add_obstacles(grid, config)

    add_exits(grid, config)

    return grid

def add_exits(grid: np.ndarray, config: EnvironmentConfig) -> None:
    """
    add the exits to the grid
    2 on the left side
    2 on the right side
    2 at the bottom side
    """
    # Left/right side: split height into gap | exit | gap | exit | gap

    gap_y = (config.height - 2 * config.exit_width) // 3
    first_exit_y_start = gap_y
    second_exit_y_start = 2*gap_y + config.exit_width

    for y in range(first_exit_y_start, first_exit_y_start + config.exit_width):
        grid[0, y] = CellType.EXIT
        grid[config.width - 1, y] = CellType.EXIT

    for y in range(second_exit_y_start, second_exit_y_start + config.exit_width):
        grid[0, y] = CellType.EXIT
        grid[config.width - 1, y] = CellType.EXIT

    # Bottom side: split width into gap | exit | gap | exit | gap
    gap_x = (config.width - 2 * config.exit_width) // 3

    first_exit_x_start = gap_x
    second_exit_x_start = 2 * gap_x + config.exit_width

    for x in range(first_exit_x_start, first_exit_x_start + config.exit_width):
        grid[x, 0] = CellType.EXIT

    for x in range(second_exit_x_start, second_exit_x_start + config.exit_width):
        grid[x, 0] = CellType.EXIT


def add_obstacles(grid: np.ndarray, config: EnvironmentConfig) -> None:
    """
    adding fences to the grid
    and 2 blocks
    """
    #first fence row in front of the stage
    grid[8:44, 57:59] = CellType.OBSTACLE
    grid[56:92, 57:59] = CellType.OBSTACLE

    #second fence row
    grid[8:44, 40] = CellType.OBSTACLE
    grid[56:92, 40] = CellType.OBSTACLE

    #lower left block
    grid[28:32, 12:28] = CellType.OBSTACLE

    #lower right block
    grid[68:72, 12:28] = CellType.OBSTACLE
def add_front_stage(grid: np.ndarray, config: EnvironmentConfig) -> None:
    """
    for the stage we use a fixed stage that is allways blocked
    Mainstage x 0-99 y 79-72
    and a small catwalk
    x 48-51 y 60 - 71
    """

    grid[0:100, 72:80] = CellType.STAGE
    grid[48:52, 60:72] = CellType.STAGE