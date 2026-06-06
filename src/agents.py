#agents and behavior

from mesa.discrete_space import CellAgent
from mesa.discrete_space.cell import Cell

class PanicAgent(CellAgent):
    def __init__(self,model):
        super().__init__(model)

        self.panic_level = 0.0
        self.speed = 1

    def step(self):
        if self.cell is None:
            return

        if self.model.fire_active and self.model.is_near_fire(self.cell):
            self.increase_panic(self.model.fire_near_panic_increase)
        if self.model.is_fire_cell(self.cell):
            self.panic_level = 1.0

        next_cell = self.choose_next_cell()

        # Agent is blocked and cannot move.
        if next_cell is None:
            self.increase_panic(self.model.blocked_panic_increase)

            if self.model.is_fire_cell(self.cell):
                self.model.kill_agent(self)

            return

        # If the agent reaches an exit, he leaves
        if self.model.is_exit_cell(next_cell):
            self.model.evacuate_agent(self)
            return

        #if the next cell has a lot of panic agents the panic of the current agent increases
        self.absorb_panic_from_cell(next_cell)

        self.move_to(next_cell)

        #on a succesfull move the agents panic decrease slighly
        self.decrease_panic(self.model.panic_decay)

    def choose_next_cell(self) -> Cell | None:

        reachable_cells = self.get_reachable_cells()

        if len(reachable_cells) == 0:

            return None

        random_move_probability = self.panic_level

        make_random_move=(self.model.random.random() < random_move_probability)

        if make_random_move:
            return self.model.random.choice(reachable_cells)

        if not self.model.fire_active:
            return self.model.random.choice(reachable_cells)

        return self.choose_best_cell_to_exit(reachable_cells)

    def get_reachable_cells(self) -> list[Cell]:
        current_cell = self.cell
        if current_cell is None:
            return []

        reachable_cell_collection = current_cell.neighborhood.select(
            lambda cell:
            self.model.is_walkable_cell(cell)
            and not self.model.is_fire_cell(cell)
            and (
                self.model.is_exit_cell(cell)
                or not cell.is_full
            )

        )

        return list(reachable_cell_collection.cells)

    def increase_panic(self, blocked_panic_increase):
        self.panic_level = min(1,self.panic_level+blocked_panic_increase)

    def absorb_panic_from_cell(self, next_cell):
        other_agents = [agent for agent in next_cell.agents if agent is not self]
        if len(other_agents) == 0:
            return

        average_panic = sum(agent.panic_level for agent in other_agents)/len(other_agents)
        panic_increase = average_panic* self.model.panic_from_other_cell_increase_value
        self.increase_panic(panic_increase)

    def decrease_panic(self, panic_decay):
        self.panic_level = max(0,self.panic_level-panic_decay)

    def choose_best_cell_to_exit(self,reachable_cells):
        best_distance = min(self.model.distance_to_exit(cell) for cell in reachable_cells)

        best_cells = [cell for cell in reachable_cells if self.model.distance_to_exit(cell) == best_distance]

        return self.model.random.choice(best_cells)


