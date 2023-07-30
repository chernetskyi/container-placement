# Container-Based Microservice Placement Optimization in Cloud

## Prerequisites

```bash
python3 -m venv env
. env/bin/activate
pip3 install --use-pep517 -r requirements.txt
```

## Usage

```
usage: place.py [-h] [--log-file LOG_FILE] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-o OUTPUT] [--seed SEED] {cp-sat,pso} scenario

Solve node-container placement.

positional arguments:
  {cp-sat,pso}          name of the solver
  scenario              scenario YAML file

options:
  -h, --help            show this help message and exit
  --log-file LOG_FILE   log file
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        logging level
  -o OUTPUT, --output OUTPUT
                        output file
  --seed SEED           random number generator seed
```

## Available solvers

- [x] CP-SAT
- [x] Particle Swarm Optimization

## Scenarios

Placement simulation script requires a scenario - YAML file with input data. Sample scenarios are provided in [`scenarios/`](scenarios/). Sample node set can be taken from [`scenarios/_infrastructure.yaml`](scenarios/_infrastructure.yaml). It is also possible to generate random scenario.

```
usage: generate_scenario.py [-h] [-m MICROS] [--minc MINC] [--maxc MAXC] [--no-data] [--mind MIND] [--maxd MAXD] [-n NODES] [-z ZONES]

Generate scenario for node-container placement.

options:
  -h, --help            show this help message and exit
  -m MICROS, --micros MICROS
                        number of microservices to generate
  --minc MINC, --min-containers MINC
                        minimum number of containers in microservice
  --maxc MAXC, --max-containers MAXC
                        maximum number of containers in microservice
  --no-data             no communication between microservices
  --mind MIND, --min-datarate MIND
                        minimum amount of data moved between two microservices
  --maxd MAXD, --max-datarate MAXD
                        maximum amount of data moved between two microservices
  -n NODES, --nodes NODES
                        number of nodes to generate
  -z ZONES, --zones ZONES
                        maximum number of zones to use
```

Lastly, a generated scenario can be piped directly to the placement simulation script.

```bash
generate_scenario.py | place.py pso -
```
