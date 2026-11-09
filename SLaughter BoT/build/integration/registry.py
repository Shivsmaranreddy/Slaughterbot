from pathlib import Path
from .common import ROOT, read_json, sha256

def model_records():
    return read_json(ROOT / 'config/models.yaml')['models']

def verify(model_id):
    records = {m['id']:m for m in model_records()}
    if model_id not in records:
        raise ValueError('Unknown model ID')
    folder = (ROOT / records[model_id]['artifact_dir']).resolve()
    if not folder.is_relative_to((ROOT / 'output/models').resolve()):
        raise ValueError('Model directory outside registry root')
    manifest = folder / 'manifest.json'
    if not manifest.exists():
        return {'id':model_id, 'status':'NOT_TRAINED', 'reason':'No export manifest'}
    m = read_json(manifest)
    if not isinstance(m, dict):
        raise ValueError('Manifest must be a JSON object')
    if m.get('status') != 'TRAINED_EXPERIMENTAL':
        return {'id':model_id, 'status':'NOT_TRAINED', 'reason':'Training has not been recorded'}
    if m.get('id') != model_id or m.get('provenance') not in ('real','synthetic','demonstration'):
        raise ValueError('Manifest identity/provenance mismatch')
    for key in ['artifact','training','evaluation']:
        if not isinstance(m.get(key), str) or not m[key]:
            raise ValueError('Artifact references must be nonempty relative paths')
        p = (folder / m[key]).resolve()
        if not p.is_relative_to(folder) or not p.is_file():
            raise ValueError('Missing or out-of-folder artifact')
    if sha256(folder / m['artifact']) != m.get('sha256'):
        raise ValueError('Artifact checksum mismatch')
    for key in ['training','evaluation']:
        evidence=read_json(folder / m[key])
        if not isinstance(evidence, dict) or not evidence:
            raise ValueError('Training/evaluation evidence must be nonempty JSON objects')
    return dict(m, folder=str(folder))

def status():
    results = []
    for m in model_records():
        try:
            results.append(verify(m['id']))
        except (ValueError, KeyError, OSError) as e:
            results.append({'id':m['id'],'status':'INVALID','reason':str(e)})
    return results
