#Mesa Model and Simulation
import numpy as np
import mesa

from mesa.discrete_space.cell import Cell
from environment import CellType
from agents import PanicAgent
#OrthogonalMooreGrid

from environment import EnvironmentConfig, create_environment_grid, create_distance_to_exit_grid

class PanicSimModel(mesa.Model):

    def __init__(self, environment_config: EnvironmentConfig, num_agents: int):
        super().__init__(seed=environment_config.random_seed)
        #cons for panic increase and decrease
        #TODO give cons a logic value
        self.blocked_panic_increase = 9999
        self.panic_decay = 9999
        self.panic_from_other_cell_increase_value = 9999


        self.num_agents = num_agents
        self.evacuated_agents = 0
        self.running = True
        self.max_steps = 10000

        #grid for the model
        self.grid = mesa.discrete_space.OrthogonalMooreGrid(
            (environment_config.width,
            environment_config.height),
            torus=False,
            capacity=environment_config.max_agents_per_cell
        )

        self.environment_config = environment_config
        self.environment_grid = create_environment_grid(environment_config)
        self.distance_to_exit_grid = create_distance_to_exit_grid(self.environment_grid)

        #TODO spawn agents in the model
    def get_cell_type(self, cell: Cell) -> CellType:
        x,y = cell.coordinate
        return CellType(self.environment_grid[x,y])

    def is_exit_cell(self, cell: Cell) -> bool:
        return self.get_cell_type(cell) == CellType.EXIT

    def is_walkable_cell(self, cell: Cell) -> bool:
        cell_type = self.get_cell_type(cell)
        return cell_type in (CellType.EXIT, CellType.FREE)

    def distance_to_exit(self, cell: Cell) -> int:
        x, y = cell.coordinate
        return int(self.distance_to_exit_grid[x, y])

    def evacuate_agent(self,agent: PanicAgent) -> None:
        self.evacuated_agents += 1
        agent.remove()
    #TODO step
    def step(self):
        pass

    # TODO run_model
    def run_model(self):
        pass
