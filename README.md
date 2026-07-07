# ising-rs

A fast, interactive 2D Ising model simulator with a Rust core and Python bindings, built with [PyO3](https://pyo3.rs) and [maturin](https://www.maturin.rs). Includes both single-spin Metropolis-Hastings and cluster-based Wolff algorithms, plus an optional PySide6 GUI for real-time visualization.

## Features

- **Fast Rust core** — spin lattice operations run as native compiled code, far outperforming a pure-Python implementation
- **Two sampling algorithms**:
  - Metropolis-Hastings (single-spin flips)
  - Wolff cluster algorithm (efficient near the critical temperature, avoids critical slowing down)
- **Configurable physics** — lattice size, temperature, and external magnetic field are all adjustable at runtime
- **Optional interactive GUI** — real-time lattice visualization with live energy/magnetization readouts, built with PySide6
- **Periodic boundary conditions** — toroidal lattice topology (standard for finite-size Ising simulations)

## Installation

Core simulation engine only:

```bash
pip install ising-rs
```

With GUI support (adds PySide6 and numpy):

```bash
pip install "ising-rs[gui]"
```

## Quick Start

```python
import ising_rs

# Create a 50x50 lattice at temperature T=2.0, zero external field
lattice = ising_rs.Lattice(width=50, height=50, temperature=2.0, h_z=0.0)

# Run 1000 Metropolis steps
for _ in range(1000):
    lattice.simulation_step()

print("Total energy:", lattice.get_energy())
print("Total magnetization:", lattice.get_total_magnetization())
print("Average magnetization:", lattice.average_magnetization())
```

### Using the Wolff Algorithm

The Wolff algorithm flips entire correlated clusters at once, converging much faster near the critical temperature (T ≈ 2.269 in reduced units where J = k_B = 1). Note: Wolff currently assumes zero external field (`h_z = 0.0`).

```python
lattice = ising_rs.Lattice(width=100, height=100, temperature=2.27, h_z=0.0)

for _ in range(20):
    lattice.wolff_step()
```

### Launching the GUI

The interactive GUI is not currently packaged as an installable command. Instead, run the provided script in the github repository directly:

```bash
python python_tests/test.py
```

This opens an interactive window showing the live lattice state, with sliders for temperature and magnetic field, a dropdown to switch between Metropolis and Wolff algorithms, and a pause/resume button.
## API Reference

### `Lattice(width, height, temperature, h_z)`

Constructs a new lattice with randomly initialized spins (±1).

| Parameter | Type | Description |
|---|---|---|
| `width` | int | Number of columns |
| `height` | int | Number of rows |
| `temperature` | float | Reduced temperature (k_B = 1, J = 1) |
| `h_z` | float | External magnetic field strength |

**Attributes:**
- `width`, `height` — read-only lattice dimensions
- `temperature` — read/write, adjustable at runtime
- `h_z` — read/write, adjustable at runtime

**Methods:**
| Method | Returns | Description |
|---|---|---|
| `simulation_step()` | `None` | Performs one Metropolis-Hastings spin-flip attempt |
| `wolff_step()` | `None` | Performs one Wolff cluster flip (h_z must be 0) |
| `get_energy()` | `float` | Total lattice energy |
| `get_energy_diff_from_flip(idx)` | `float` | Energy change if the spin at `idx` were flipped |
| `get_total_magnetization()` | `float` | Sum of all spins |
| `average_magnetization()` | `float` | Total magnetization divided by lattice size |
| `as_array()` | `list[int]` | Flat list of spins (row-major order) |
| `get_nearest_neighbors(idx)` | `list[int]` | Indices of the 4 periodic nearest neighbors |

## Physics Background

This implements the classical 2D Ising model on a square lattice with periodic (toroidal) boundary conditions. The Hamiltonian is:

```
H = -J * sum(s_i * s_j for neighboring pairs) - h * sum(s_i)
```

with `J = 1` (ferromagnetic coupling) and reduced units where the Boltzmann constant `k_B = 1`. This means `temperature` is expressed in the same energy units as `J`, not in Kelvin — this is the standard convention in computational statistical mechanics.

At zero external field (`h_z = 0`), the model exhibits a genuine second-order phase transition at the critical temperature `T_c ≈ 2.269`. Below `T_c`, the system spontaneously magnetizes into large aligned domains; above `T_c`, thermal fluctuations disorder the spins. Applying any nonzero external field breaks the up/down symmetry and removes this sharp transition, smoothing it into a continuous crossover.

## Development

This project uses [maturin](https://www.maturin.rs) to build the Rust extension.

```bash
git clone https://github.com/leonardbajusz/isingmodel.git
cd isingmodel
maturin develop
```

Requires Rust (via [rustup](https://rustup.rs)) and Python 3.9+.

## License

MIT
