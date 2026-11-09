# Four AI models

## Independent model responsibilities

Model | Input | Output
Visual CNN | Permitted labelled images | Visible-condition assessment
Volume autoencoder | Aligned 32³ volumes | Experimental reconstruction
Scenario PPO | Synthetic challenge context | Scenario choice
Robot PPO | Synthetic task observations | Task-action suggestion

## Training and evidence

Each model has its own configurable notebook and export folder.

Exports record training, evaluation, provenance and file checksums.

Visual labels and real scan geometry require independent review.

## Scientific limits

Image classification cannot establish food safety.

Synthetic ellipsoids do not validate ultrasound anatomy.

All four model slots remain NOT TRAINED until their notebooks run.