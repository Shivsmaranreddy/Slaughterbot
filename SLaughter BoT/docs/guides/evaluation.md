# Experimental design and evaluation

## Visual experiment
Split by original batch/subject before augmentation. Establish a simple majority-class baseline.
Train the MobileNet baseline, select checkpoints using validation loss and evaluate the untouched
test split once. Report per-class precision, recall, macro F1, confusion matrix and sample counts.
Study confidence calibration, coverage and lighting/device shift separately. The code includes
uncalibrated coverage at a provisional threshold, not a validated safety decision rule.

## Volume experiment
Use separate phantom or subject groups. Compare test MSE with the constant-mean baseline and
inspect spatial errors. Report source geometry and normalization. Synthetic reconstruction alone
cannot validate real ultrasound performance. Independent physical phantoms are a later requirement.

## Dual RL experiment
Train scenario PPO and compare its held-out rewards with random and rule generators. Train robot
PPO with randomized scenarios, optionally conditioned by the exported scenario policy. Train a
narrow-scenario PPO baseline with the same budget. Evaluate all robot policies on the same held-out
seed range 10000–10049. Record completion rate, mean steps, movement, invalid requests and actual
simulated limit violations. A rejected unsafe suggestion counts as invalid, not as physical violation.
Repeat each condition with several seeds. Report differences and uncertainty rather than selecting
only the best run. Simulator steps do not substitute for physical timing measurements.

## Current results
NOT RUN. There are no accuracy, reconstruction, timing, generalization or physical-safety results yet.
Source checks can identify syntax errors but cannot establish runtime behavior or exhibition readiness.
