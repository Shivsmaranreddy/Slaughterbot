from pathlib import Path
from build.integration.common import read_json, sha256

def validate_manifest(path, root, required_modality='image'):
    m = read_json(path)
    required = ['name','source','license','citation','modality','provenance','collection_method','limitations','samples']
    if any(not m.get(k) for k in required):
        raise ValueError('Manifest is missing required provenance or samples')
    if m['license'] in ('UNKNOWN','REVIEW_REQUIRED') or m.get('permission_confirmed') is not True:
        raise ValueError('Dataset permission must be confirmed before training')
    if m['modality'] != required_modality or m['provenance'] not in ('real','synthetic','demonstration'):
        raise ValueError('Incorrect modality or provenance')
    root = Path(root).resolve()
    groups, hashes = {}, set()
    splits = {'train':0,'val':0,'test':0}
    for sample in m['samples']:
        split = sample['split']
        if split not in splits:
            raise ValueError('Split must be train, val or test')
        p = (root / sample['path']).resolve()
        if not p.is_relative_to(root) or not p.is_file():
            raise ValueError('Missing file or path outside data root')
        digest = sha256(p)
        if digest != sample['sha256'] or digest in hashes:
            raise ValueError('Checksum mismatch or duplicate sample')
        hashes.add(digest)
        group = sample['group_id']
        if not group or (group in groups and groups[group] != split):
            raise ValueError('Subject/batch group leakage between splits')
        groups[group] = split
        if sample.get('provenance') != m['provenance']:
            raise ValueError('Mixed provenance is not allowed in one manifest')
        splits[split] += 1
    if not all(splits.values()):
        raise ValueError('Nonempty train, validation and test sets required')
    return m
