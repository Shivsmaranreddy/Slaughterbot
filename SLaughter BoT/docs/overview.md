# Project overview and abstract

SLAUGHTER BOT explores a software-first assistance system for operational recordkeeping,
experimental visual condition assessment, aligned-volume representation learning and safe
robotics simulation. The exhibition uses only harmless inert objects. The name does not imply
autonomous slaughtering: no cutting or production meat-handling mechanism is implemented.

## Problem statement
The project investigates whether a small, transparent software system can demonstrate linked
inventory records, order workflows and independently evaluated AI components at school scale.
Claims about actual MSME demand, cost savings or business adoption remain hypotheses until studied.

## Proposed solution and working principle
Two local interfaces share a backend and database. Independent model adapters provide experimental
outputs and abstentions. A scenario policy can generate synthetic training conditions for a task
policy. A separate safety controller validates every mock movement. Training happens in user-run
notebooks, and exported model manifests document what was trained and evaluated.

## Technical specifications
Python 3.11–3.12, FastAPI, SQLite, browser-native HTML/JavaScript; optional PyTorch, Gymnasium and
Stable Baselines3 training. No local GPU requirement for the mock app. A small Arduino servo gate
is the proposed physical demonstrator, subject to later hardware review and testing.

## Originality
The contribution is the student's implementation, documented experiments, integration and comparison
of baseline and learned control in a transparent exhibition system. CNNs, autoencoders, PPO, management
software and sorting gates are established approaches. This project makes no claim to invent them.
