from pathlib import Path
import hashlib, json, random

ROOT = Path(__file__).resolve().parents[2]

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False), encoding='utf-8')

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def seed_all(seed):
    import numpy as np
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def finalize(folder, model_id, artifact, training, evaluation, preprocessing, provenance):
    folder = Path(folder)
    if not Path(artifact).is_file() or not evaluation:
        raise ValueError('Artifact and evaluation required')
    import importlib.metadata
    versions = {}
    for package in ['torch','torchvision','numpy','gymnasium','stable-baselines3']:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pass
    write_json(folder / 'evaluation.json', evaluation)
    write_json(folder / 'training.json', dict(training, package_versions=versions))
    write_json(folder / 'manifest.json', {
        'id':model_id,'version':'0.1.0','status':'TRAINED_EXPERIMENTAL',
        'artifact':Path(artifact).name,'sha256':sha256(artifact),
        'training':'training.json','evaluation':'evaluation.json',
        'preprocessing':preprocessing,'provenance':provenance,
        'limitations':['Experimental; evaluation applies only to the recorded dataset/simulator.']})
