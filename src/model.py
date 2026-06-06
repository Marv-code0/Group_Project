#Mesa Model and Simulation
import numpy as np
import mesa

from mesa.discrete_space.cell import Cell
from mesa.datacollection import DataCollector
from environment import CellType
from agents import PanicAgent
#OrthogonalVonNeumannGrid

from environment import EnvironmentConfig, create_environment_grid, create_distance_to_exit_grid,create_distance_to_stage_grid

class PanicSimModel(mesa.Model):

    def __init__(self, environment_config: EnvironmentConfig, num_agents: int):
        super().__init__(rng=environment_config.random_seed)
        #cons for panic increase and decrease

        self.blocked_panic_increase = environment_config.blocked_panic_increase
        self.panic_decay = environment_config.panic_decay
        self.panic_from_other_cell_increase_value = environment_config.panic_from_other_cell_increase_value
        self.fire_near_panic_increase = environment_config.fire_near_panic_increase


        self.num_agents = num_agents
        self.evacuated_agents = 0


        self.dead_agents = 0
        self.running = True
        self.max_steps = 10000

        #grid for the model
        self.grid = mesa.discrete_space.OrthogonalVonNeumannGrid(
            (environment_config.width,
             environment_config.height),
            torus=False,
            capacity=environment_config.max_agents_per_cell,
            random=self.random
        )

        self.environment_config = environment_config
        self.environment_grid = create_environment_grid(environment_config)
        self.distance_to_exit_grid = create_distance_to_exit_grid(self.environment_grid)
        self.distance_to_stage_grid = create_distance_to_stage_grid(self.environment_grid)

        #fire logic
        self.fire_grid = np.full(
            (environment_config.width, environment_config.height),
            False,
            dtype=bool
        )
        self.fire_active = False
        self.fire_start_step = environment_config.fire_start_step


        self.spawn_agents()
        #datacollector
        self.datacollector = DataCollector(
            model_reporters={
                "evacuated_agents": "evacuated_agents",
                "dead_agents": "dead_agents",
                "active_agents": lambda model: len(model.agents),
                "fire_cells": lambda model: int(np.sum(model.fire_grid)),
                "average_panic": lambda model: (
                    sum(agent.panic_level for agent in model.agents) / len(model.agents)
                    if len(model.agents) > 0
                    else 0
                ),
            },
            agent_reporters={
                "panic_level": "panic_level",
            }
        )



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

    def step(self) -> None:

        if self.steps >= self.fire_start_step and not self.fire_active:
            self.start_fire()

        if (self.fire_active and self.steps > self.fire_start_step
                and self.steps % self.environment_config.fire_spread_interval == 0
        ):
            self.spread_fire()
        self.agents.shuffle_do("step")

        if self.evacuated_agents + self.dead_agents >= self.num_agents or self.steps >= self.max_steps:
            self.running = False

        self.datacollector.collect(self)

    def run_model(self):
        while self.running:
            self.step()

    def spawn_agents(self):
        for _ in range(self.num_agents):
            spawn_cells = self.grid.all_cells.select(self.is_spawn_cell)

            if len(spawn_cells) == 0:
                raise RuntimeError('No free cells available')

            agent = PanicAgent(self)
            agent.cell = spawn_cells.select_random_cell()

    def is_spawn_cell(self, cell: Cell) -> bool:
        if not self.is_walkable_cell(cell):
            return False
        if self.is_exit_cell(cell):
            return False

        if cell.is_full:
            return False

        x,y = cell.coordinate

        border_protection = self.environment_config.border_spawn_protection

        return (border_protection <= x < self.environment_config.width - border_protection and
                border_protection <= y < self.environment_config.height - border_protection)

    def is_fire_cell(self, cell: Cell) -> bool:
        x, y = cell.coordinate
        return bool(self.fire_grid[x, y])

    def start_fire(self):
        possible_fire_cells = self.grid.all_cells.select(
            lambda firecell:
            self.is_walkable_cell(firecell) and not self.is_exit_cell(firecell)
        )

        start_cell = possible_fire_cells.select_random_cell()

        fire_neighbors = start_cell.neighborhood.select(
            lambda firecell:
            self.is_walkable_cell(firecell) and not self.is_exit_cell(firecell)
        )

        fire_cells = [start_cell] + list(fire_neighbors.cells)
        fire_cells = fire_cells[:self.environment_config.fire_start_size]

        for cell in fire_cells:
            x,y = cell.coordinate
            self.fire_grid[x,y] = True

        self.fire_active = True

    def kill_agent(self,agent: PanicAgent) -> None:
        self.dead_agents += 1
        agent.remove()

    def spread_fire(self) -> None:
        possible_new_fire_cells = []

        fire_cells = self.grid.all_cells.select(self.is_fire_cell)

        for fire_cell in fire_cells.cells:
            neighbor_cells = fire_cell.neighborhood.select(
                lambda neighbor:
                self.is_walkable_cell(neighbor)
                and not self.is_exit_cell(neighbor)
                and not self.is_fire_cell(neighbor)
            )

            possible_new_fire_cells.extend(neighbor_cells.cells)

        if len(possible_new_fire_cells) == 0:
            return

        spread_size = min(
            len(possible_new_fire_cells),
            self.environment_config.fire_spread_size
        )

        new_fire_cells = self.random.sample(
            possible_new_fire_cells,
            spread_size
        )

        for cell in new_fire_cells:
            x, y = cell.coordinate
            self.fire_grid[x, y] = True

    def is_near_fire(self,cell: Cell) -> bool:
        return any(self.is_fire_cell(neighbor) for neighbor in cell.neighborhood.cells)

    def distance_to_stage(self, cell: Cell) -> int:
        x, y = cell.coordinate
        return int(self.distance_to_stage_grid[x, y])