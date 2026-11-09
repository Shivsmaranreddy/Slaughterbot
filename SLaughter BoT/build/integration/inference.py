from pathlib import Path
from .registry import verify
from .common import ROOT

NOTICE = 'Experimental assessment only. This does not establish food safety.'

def infer(model_id, payload):
    try:
        info = verify(model_id)
    except (ValueError, OSError, KeyError) as e:
        return {'model_id':model_id,'status':'ABSTAIN','reason':str(e),'notice':NOTICE}
    if info['status'] != 'TRAINED_EXPERIMENTAL':
        return {'model_id':model_id,'status':'ABSTAIN','reason':'Model NOT TRAINED','notice':NOTICE}
    folder = Path(info['folder'])
    try:
        if model_id == 'model_1_visual_cnn':
            from build.imagery.cnn.pipeline import predict
            result = predict(folder, payload['image_path'])
        elif model_id == 'model_2_ultrasound_3d':
            from build.imagery.ultrasound_3d.pipeline import predict
            result = predict(folder, payload['volume_path'])
        else:
            import numpy as np
            from stable_baselines3 import PPO
            obs = np.asarray(payload['observation'], dtype=np.float32)
            model = PPO.load(folder / info['artifact'], device='cpu')
            if not model.observation_space.contains(obs):
                raise ValueError('Observation incompatible with model')
            action, _ = model.predict(obs, deterministic=True)
            result = {'status':'EXPERIMENTAL','suggested_action':int(action),
                      'role':'scenario_generation' if model_id.endswith('environment_rl') else 'task_control'}
        return dict(result, model_id=model_id, provenance=info['provenance'], notice=NOTICE)
    except Exception as e:
        # Fail closed for incompatible optional dependencies and invalid trusted model exports.
        return {'model_id':model_id,'status':'ABSTAIN','reason':str(e),'notice':NOTICE}

def fuse(results):
    # Typed evidence bundle, not an arithmetic average of unrelated scores.
    perception = [r for r in results if r.get('model_id') in ('model_1_visual_cnn','model_2_ultrasound_3d')]
    policies = [r for r in results if r.get('model_id') in ('model_3_environment_rl','model_4_robotic_rl')]
    return {'perception':perception,'policy_suggestions':policies,
            'decision':'HUMAN_REVIEW','food_safety_certified':False,'notice':NOTICE}
