# Container-Based Microservice Placement Optimization in Cloud

## Prerequisites

```bash
python3 -m venv env
. env/bin/activate
pip3 install -r requirements.txt
```

## Usage

```
usage: place.py [-h] [--seed SEED] {pso,cp-sat} filename

Solve node-container placement.

positional arguments:
  {cp-sat,pso}  name of the solver to use
  filename      path to YAML file with the scenario

options:
  -h, --help    show this help message and exit
  --seed SEED   value to initialize the random number generator
```

## Available solvers

- [x] CP-SAT
- [x] Particle Swarm Optimization
