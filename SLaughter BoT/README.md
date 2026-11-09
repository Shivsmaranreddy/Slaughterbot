# SLAUGHTER BOT

CBSE Science Exhibition 2026–27. An experimental software and inert-object robotics project.

## Delivery status

This is a source-file delivery. No dependencies were installed, no application was started,
and no AI training was performed during preparation. All four model slots are **NOT TRAINED**.
Python/notebook syntax and artifact structure are checked separately from runtime tests.
See `prep/project_tracking/progress_tracker.md` for implemented files and remaining validation.

## Start here

1. Read `docs/guides/training.md` and `docs/guides/dataset_contract.md`.
2. Upload this repository to Colab or Kaggle. Open a module's `train.ipynb`.
3. Set `REPO_ROOT` and data locations in the notebook. Run its install cell there.
4. Train and evaluate each model independently. Save generated model folders somewhere persistent.
5. Bring back the complete model folders, including metadata, evaluation and checksums.
6. Follow `docs/guides/model_handoff.md`. Never rename arbitrary files to impersonate trained models.

When you choose to run the local app later (Python 3.11 or 3.12 recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:SB_MANAGER_TOKEN = 'choose-a-long-random-local-token'
python -m uvicorn build.backend.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/customer` and `http://127.0.0.1:8000/manager`.
Use fictional data only. This local demonstration has token-protected manager routes,
not production customer identity, tenant isolation or subscription billing.

## Main folders

| Folder | Responsibility |
|---|---|
| build | Source code, model notebooks, backend, interfaces and firmware |
| config | Editable settings and model registry |
| docs | Architecture, guides and exhibition material |
| prep | Existing solutions, research, judge preparation and trackers |
| output | Generated data, models, results and deployment artifacts |
| scripts | Explicit utilities; nothing installs or trains automatically |
| tests | Automated tests to run when you choose to install dependencies |

## Boundaries

Visual assessment cannot certify food safety. Synthetic volume reconstruction cannot establish
anatomical accuracy. The scenario generator and robotic policy have different responsibilities.
Random scenario generation is not a trained RL model. Hardware may only position harmless inert
objects with a low-force mechanism and independent emergency stop. No slaughtering, cutting,
or production meat-handling mechanism is included.

## Validation later

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
python scripts/verify_models.py
```

Missing models yield explicit abstentions. Downloading pretrained backbones in a training notebook
does not make this project's classifier trained. No dataset or model performance is claimed here.
