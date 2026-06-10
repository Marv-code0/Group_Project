# Mass Panic Simulation

Small Mesa project for a simplified crowd and panic simulation in an arena.

Agents first move towards the stage. After a fire starts, they try to evacuate. The fire spreads through the grid and agents avoid burning cells if possible. Panic starts after the fire is active. Panic can increase because of nearby fire, blocked movement or other panicked agents.

## Setup

Tested with Python 3.14.
We recommend Python 3.12 or higher. 
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run simulation

```bash
source .venv/bin/activate
python src/main.py
```

## Run visualization

```bash
source .venv/bin/activate
solara run src/visualization.py
```

Open:

```text
http://localhost:8765
```

## EnvironmentConfig values

These values can be changed in `main.py` and `visualization.py`.

```
exit_width
use_stage
use_barriers
random_seed
max_agents_per_cell
border_spawn_protection
fire_start_step
fire_start_size
fire_spread_interval
fire_spread_size
blocked_panic_increase
panic_decay
panic_from_other_cell_increase_value
fire_near_panic_increase
```

Short explanation:

- `exit_width`: width of the exits.
- `use_stage`: enables/disables the stage.
- `use_barriers`: enables/disables fences and obstacles.
- `random_seed`: seed so the simulation is reproducible.
- `max_agents_per_cell`: how many agents can stand on one cell.
- `border_spawn_protection`: distance from the border where no agents spawn at the start.
- `fire_start_step`: step when the fire starts.
- `fire_start_size`: number of cells that start burning.
- `fire_spread_interval`: after how many steps the fire spreads again.
- `fire_spread_size`: how many new cells can start burning per spread.
- `blocked_panic_increase`: panic increase if an agent is blocked after the fire started.
- `panic_decay`: panic decrease after a successful move.
- `panic_from_other_cell_increase_value`: how much panic spreads from agents in the next cell.
- `fire_near_panic_increase`: panic increase if fire is near the agent.

If an agent has `panic_level = 1.0`, the chance for a random move is `50%`. Lower panic means a lower random move chance.

## Files

```text
src/environment.py     Arena, CellTypes, exits, obstacles, stage, preference grid and distance grids
src/agents.py          Agent behavior
src/model.py           Mesa model, fire logic, safe exit distances and DataCollector
src/main.py            Normal simulation run
src/visualization.py   Solara visualization
```
## Note 
Don't try this simulation if you plan a real concert. This might not be safe. Thank you.