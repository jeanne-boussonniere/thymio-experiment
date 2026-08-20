# Thymio experiments

Swarm robotics experiments with Thymio robots, built as part of an internship on the **SCA algorithm** (Scarcity-Cascade Authority algorithm).

This repository contains the **behaviours** (pure logic) and the **experiments** (async execution loop that drives a physical robot) run on the Thymios' onboard Raspberry Pi, through the third-party [`swarm_platform`](https://github.com/lmschw/thymio_swarm_platform) platform.

The simulations of the same algorithms can be found on the [`decision_making_simulation`](https://github.com/jeanne-boussonniere/decision_making_simulation) repository.


## Table of contents

- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Configuration](#configuration-swarm_projectyaml)
- [Available experiments](#available-experiments)
- [Running an experiment](#running-an-experiment)
- [Output data](#output-data)

## Project structure

```
thymio-experiment/
├── behaviours/              # Pure logic, independent of the robot 
│   ├── obstacle_avoidance.py  # Obstacle avoidance 
│   ├── color_recognition.py   # Floor color patch detection
│   ├── sca_algorithm_1.py     # SCA - IR communication variant 
│   ├── sca_algorithm_2.py     # SCA - Optitrack variant
│   └── quorum_sensing.py      # Quorum sensing - majority-vote opinion algorithm
├── experiments/              # Async execution loops
│   ├── obstacle_avoidance.py
│   ├── color_recognition.py
│   ├── messaging_test.py      # UDP connectivity test 
│   ├── sca_algorithm_1.py
│   ├── sca_algorithm_2.py
│   └── quorum_sensing.py
├── utils/
│   └── communication.py       # SwarmUDPManager - inter-robot UDP messaging
└── swarm_project.yaml         # Experiment declarations for swarm_platform
```

Each experiment combines one or more behaviours (`behaviours/`) with the robot's I/O calls (sensors, motors, network). 

## Requirements

- One or more Thymio robots fitted with Raspberry Pi
- The [`swarm_platform`](https://github.com/lmschw/thymio_swarm_platform) platform installed on each Pi. This repository cannot run without it
- The Raspberry Pi units and the control machine on the same Wi-Fi network 
- For `sca_algorithm_2` and `quorum_sensing`: an Optitrack system reachable on the network

## Configuration (`swarm_project.yaml`)

This file declares the experiments exposed to `swarm_platform`, along with
the Optitrack tracking configuration.

```yaml
tracking:
  host: 10.0.10.4
  hostname_map:
    thymio-11: "RigidBody 19"
    ...

experiments:
  sca_algorithm_2:
    class: experiments.sca_algorithm_2.SCAExperiment
    tracking: true   # enables Optitrack pose retrieval for this experiment
```

To add a new experiment, just add an entry under `experiments:` pointing to the corresponding class.

## Available experiments

| Name (yaml)          | Class                                          | Purpose |
|-----------------------|--------------------------------------------------|------|
| `obstacle_avoidance` | `experiments.obstacle_avoidance.ObstacleAvoidanceExperiment` | Obstacle avoidance alone |
| `color_recognition`  | `experiments.color_recognition.ColorRecognitionExperiment`   | Obstacle avoidance + floor color detection |
| `messaging_test`     | `experiments.messaging_test.MessagingTestExperiment`          | Checks UDP connectivity between robots in the swarm |
| `sca_algorithm_1`    | `experiments.sca_algorithm_1.SCAExperiment`                   | SCA with neighbour estimation via IR communication |
| `sca_algorithm_2`    | `experiments.sca_algorithm_2.SCAExperiment` | SCA with Optitrack positions |
| `quorum_sensing`     | `experiments.quorum_sensing.QuorumSensingExperiment`  | Majority-vote opinion algorithm: adopts a neighbour opinion once it's held by more than 60% of nearby robots |


## Running an experiment

Actual execution (robot selection, start/stop, log streaming) is handled by [`swarm_platform`](https://github.com/lmschw/thymio_swarm_platform). Refer to its documentation for more information. 

## Output data
 
| Column | Meaning | Present in |
|--------|---------|------------|
| `proximity`| Values of the 5 front and 2 back sensors | All except messaging_test |
| `reflected` | Values of the 2 floor sensors | SCA, quorum sensing and color recognition |
| `tick` | Step counter | SCA and quorum sensing |
| `left_motor` | Speed of the left wheel | All except messaging_test |
| `right_motor` | Speed of the right wheel | All except messaging_test |
| `patch` | Index of the patch the robot is currently on (-1 if none) | SCA and quorum sensing |
| `color` | Name of the color the robot is on | Color recognition only |
| `opinion` | Index of the patch the robot currently believes is best (-1 if none yet) | SCA and quorum sensing |
| `quality` | Robot's estimate of its opinion patch's quality | SCA only |
| `rarity` | How rare the robot's opinion is among its recently-seen neighbours | SCA only |
| `authority` | Robot's current authority | SCA only |
| `buffer` | Robot's current buffer with the last robots it saw, their opinion and when it saw them | SCA only |
| `neighbours` | List of neighbours' hostnames | SCA-2 and quorum sensing|
| `rx` | IR message received with a neighbour's id | SCA-1 only |
| `position` | Coordinates (x,y,z) of the robot given by Optitrack | SCA-2 and quorum sensing |
| `hostnames` | Name of the robot added automatically by the platform logger | All |

`messaging_test` only logs the messages received and the hostnames


