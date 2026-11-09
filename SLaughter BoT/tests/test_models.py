import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env
from build.rl.robotic_control.environment import SortingEnv, rule_action
from build.rl.environment_generator.environment import ScenarioEnv
from build.imagery.ultrasound_3d.pipeline import load_volume, Autoencoder
from build.imagery.cnn.pipeline import network, transform
import torch
from PIL import Image

def test_env_contracts():
    check_env(SortingEnv(),skip_render_check=True)
    check_env(ScenarioEnv(),skip_render_check=True)

def test_seed_and_safety():
    a,b=SortingEnv(),SortingEnv()
    assert np.array_equal(a.reset(seed=13)[0],b.reset(seed=13)[0])
    for action in [2,0,1]:
        oa,ra,ta,xa,ia=a.step(action); ob,rb,tb,xb,ib=b.step(action)
        assert np.array_equal(oa,ob) and (ra,ta,xa,ia)==(rb,tb,xb,ib)
        assert not ia['safety_violation']
        if ta or xa: break

def test_rule_completes_clean_environment():
    env=SortingEnv(randomized=False); obs,_=env.reset(seed=42)
    for _ in range(20):
        obs,_,term,trunc,info=env.step(rule_action(obs))
        if term or trunc: break
    assert info['success']

def test_preprocessing_and_forward():
    x=transform()(Image.new('RGB',(40,60)))
    assert x.shape==(3,224,224) and torch.isfinite(x).all()
    model=network(2); model.eval()
    with torch.no_grad(): assert model(x[None]).shape==(1,2)
    ae=Autoencoder()
    with torch.no_grad(): assert ae(torch.zeros(1,1,32,32,32)).shape==(1,1,32,32,32)

def test_invalid_scan_geometry(tmp_path):
    p=tmp_path/'volume.npz'
    np.savez(p,volume=np.zeros((32,32,32)),spacing_mm=[1,0,1],orientation=np.eye(3))
    with pytest.raises(ValueError,match='spacing'): load_volume(p)
