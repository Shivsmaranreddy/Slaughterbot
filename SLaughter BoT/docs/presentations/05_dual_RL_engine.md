# Dual RL engine

## Two learning responsibilities

Scenario PPO selects target and disturbance combinations.

Robot PPO observes the current synthetic state and proposes actions.

Random and rule-based generation remain explicit baselines.

## Experiment pipeline

Scenario choice

Robot training

Held-out tests

Policy export

## Generalization experiment

Compare randomized training with a narrow-scenario PPO baseline.

Use the same held-out evaluation seeds and training budgets.

Report completion, steps, movement, invalid actions and safety violations.