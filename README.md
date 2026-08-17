# thymio-experiment

Swarm robotics experiments with Thymio robots, built as part of an
internship on the **SCA** algorithm (Scarcity-Cascade Authority algorithm).

This repository contains the **behaviours** (pure logic)
and the **experiments** (async execution loop that drives a physical robot)
run on the Thymios' onboard Raspberry Pi, through the third-party
[`swarm_platform`](https://github.com/lmschw/thymio_swarm_platform) platform.


## Table of contents

- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Configuration](#configuration-swarm_projectyaml)
- [Available experiments](#available-experiments)
- [Running an experiment](#running-an-experiment)

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

Each experiment combines one or more behaviours (`behaviours/`) with the
robot's I/O calls (sensors, motors, network). 

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

To add a new experiment, just add an entry under `experiments:` pointing to
the corresponding class.

## Available experiments

| Name (yaml)          | Class                                          | Purpose |
|-----------------------|--------------------------------------------------|------|
| `obstacle_avoidance` | `experiments.obstacle_avoidance.ObstacleAvoidanceExperiment` | Obstacle avoidance alone |
| `color_recognition`  | `experiments.color_recognition.ColorRecognitionExperiment`   | Obstacle avoidance + floor color detection |
| `messaging_test`     | `experiments.messaging_test.MessagingTestExperiment`          | Checks UDP connectivity between robots in the swarm |
| `sca_algorithm_1`    | `experiments.sca_algorithm_1.SCAExperiment`                   | SCA with neighbour estimation via IR communication |
| `sca_algorithm_2`    | `experiments.sca_algorithm_2.SCAExperiment` | SCA with Optitrack positions|
| `quorum_sensing`     | `experiments.quorum_sensing.QuorumSensingExperiment`  | Majority-vote opinion algorithm: adopts a neighbour opinion once it's held by more than 60% of nearby robots |


## Running an experiment

Actual execution (robot selection, start/stop, log streaming) is handled by
[`swarm_platform`](https://github.com/lmschw/thymio_swarm_platform). Refer to its documentation for more information. 




