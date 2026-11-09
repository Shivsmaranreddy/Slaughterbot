import json, math
import pytest
from build.hardware.controller import SafetyController
from build.integration.inference import infer, fuse
from build.integration.registry import model_records, status
from build.imagery.cnn.data import validate_manifest
from build.integration.common import sha256

def test_missing_model_abstains():
    result=infer('model_1_visual_cnn',{})
    assert result['status']=='ABSTAIN'
    assert 'NOT TRAINED' in result['reason']

def test_four_distinct_registry_roles():
    assert len(model_records())==4
    assert len({m['type'] for m in model_records()})==4

def test_safety_stop_and_bounds():
    c=SafetyController()
    assert not c.execute(2,1)['accepted']
    c.arm_mock()
    for _ in range(2): assert c.execute(2,1)['accepted']
    assert c.position==4 and not c.execute(2,1)['accepted']
    c.stop(); assert not c.execute(0,1)['accepted']
    assert c.position==4

@pytest.mark.parametrize('action,confidence',[(True,1),(3,1),(1,float('nan')),(1,float('inf')),(1,.79),(1,1.1),(1,True)])
def test_invalid_commands(action,confidence):
    c=SafetyController(); c.arm_mock()
    assert not c.execute(action,confidence)['accepted']
    assert c.position==2

def test_fusion_keeps_roles_separate():
    r=fuse([{'model_id':'model_1_visual_cnn','status':'ABSTAIN'}, {'model_id':'model_4_robotic_rl','suggested_action':2}])
    assert len(r['perception'])==len(r['policy_suggestions'])==1
    assert r['decision']=='HUMAN_REVIEW' and not r['food_safety_certified']

def manifest(tmp_path):
    rows=[]
    for index,split in enumerate(['train','val','test']):
        p=tmp_path/f'{index}.bin'; p.write_bytes(bytes([index]))
        rows.append({'path':p.name,'sha256':sha256(p),'group_id':str(index),'split':split,'provenance':'real'})
    data={'name':'fixture','source':'test','license':'CC0-1.0','citation':'test fixture','modality':'image',
          'provenance':'real','permission_confirmed':True,'collection_method':'unit fixture','limitations':'not image data','samples':rows}
    p=tmp_path/'manifest.json'; p.write_text(json.dumps(data)); return p,data

def test_manifest_group_leakage(tmp_path):
    p,m=manifest(tmp_path); validate_manifest(p,tmp_path)
    m['samples'][1]['group_id']='0'; p.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='leakage'): validate_manifest(p,tmp_path)

def test_manifest_provenance(tmp_path):
    p,m=manifest(tmp_path); m['samples'][2]['provenance']='synthetic'; p.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='provenance'): validate_manifest(p,tmp_path)

def test_manifest_checksum(tmp_path):
    p,m=manifest(tmp_path); (tmp_path/'0.bin').write_bytes(b'changed')
    with pytest.raises(ValueError,match='Checksum'): validate_manifest(p,tmp_path)
