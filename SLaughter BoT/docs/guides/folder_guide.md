# Folder guide

config stores settings and model records separately from code. Current YAML files use JSON syntax,
which is a valid YAML subset. Registry loading consumes models.yaml. Training defaults also appear
in notebook function calls, which are the active experiment settings; training.yaml is a planning
reference, not a hidden override. Safety hard bounds in code cannot be relaxed by editing a file.

output/datasets: manifests and generated/processed data. Keep large raw data outside Git.
output/checkpoints: resumable training weights, optimizer state and progress.
output/evaluation: measured reports and comparisons after experiments actually run.
output/experiment_logs: settings, training histories, seeds and execution events.
output/visualizations: generated plots, saliency and volume views.
output/models: canonical trained artifacts and their provenance/evaluation metadata.
output/exported_models: optional deployment-format derivatives; no ONNX conversion is claimed yet.
output/deployment: local database and future packages/configuration bundles.
output/hardware_firmware: compiled firmware only after successful compilation; editable sources are in build/hardware.
scripts: utilities explicitly invoked by the user, with no automatic installation or training.
tests: tests to run in a prepared environment; their presence does not mean they have passed.
