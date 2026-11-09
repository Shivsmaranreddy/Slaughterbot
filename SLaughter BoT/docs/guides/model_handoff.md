# Returning your trained models

Download the COMPLETE model folder from each notebook, not just weights. Keep the generated
manifest.json, training.json, evaluation.json and weights.pt or policy.zip together.
Place them under the matching output/models/model_N_* directory, replacing its NOT_TRAINED
manifest only after retaining a backup. Then run `python scripts/verify_models.py`.

Verification checks model ID, status, provenance, safe paths, artifact checksum and nonempty
training/evaluation files. A matching checksum proves file integrity, not scientific validity.
Review results and dataset permissions yourself. Only load artifacts you created or explicitly trust.
Stable Baselines policy ZIP files may contain serialized Python objects.

The inference loader checks manifests dynamically. It does not require manually changing a status
flag in config/models.yaml. Missing/invalid models abstain. Loading is on demand; trained inference
requires the training dependencies in the inference environment. No global cache hides changed files.

Visual scores are uncalibrated, and an abstention threshold is not an out-of-distribution detector.
Unfamiliar images can still yield confident errors. Volume MSE measures reconstruction only.
Policy actions are suggestions and never bypass the deterministic safety controller.
