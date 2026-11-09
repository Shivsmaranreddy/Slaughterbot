from pathlib import Path
import json
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from gymnasium.utils.env_checker import check_env
from build.integration.common import ROOT, finalize, write_json
from build.rl.robotic_control.environment import SortingEnv, rule_action
from build.rl.environment_generator.environment import ScenarioEnv

def evaluate(model, env_factory, seeds=range(10000,10050), rule=False):
    episodes=[]; trajectories=[]
    for seed in seeds:
        env=env_factory(); obs,_=env.reset(seed=seed); reward_sum=0; invalid=0; violations=0; movement=0
        for step in range(20):
            before=obs.copy()
            action=rule_action(obs) if rule else int(model.predict(obs,deterministic=True)[0])
            obs,reward,term,trunc,info=env.step(action)
            movement+=abs(float(obs[0])-float(before[0]))*4 if len(obs)==7 else 0
            reward_sum+=reward; invalid+=int(info.get('invalid_action',False)); violations+=int(info.get('safety_violation',False))
            trajectories.append({'scenario_id':f'eval-{seed}','timestep':step,'state':before.tolist(),
                'observation':before.tolist(),'action':int(action),'reward':reward,'next_state':obs.tolist(),
                'terminated':term,'truncated':trunc,'seed':seed,'provenance':'synthetic'})
            if term or trunc: break
        episodes.append({'seed':seed,'success':bool(info['success']),'steps':step+1,'reward':reward_sum,
                         'invalid_actions':invalid,'safety_violations':violations,'movement':movement})
        env.close()
    summary={'episodes':len(episodes),'completion_rate':float(np.mean([e['success'] for e in episodes])),
             'mean_steps':float(np.mean([e['steps'] for e in episodes])),
             'mean_movement':float(np.mean([e['movement'] for e in episodes])),
             'invalid_action_rate':sum(e['invalid_actions'] for e in episodes)/sum(e['steps'] for e in episodes),
             'safety_violations':sum(e['safety_violations'] for e in episodes),
             'mean_return':float(np.mean([e['reward'] for e in episodes])),
             'timing_note':'Steps are simulator time; no physical execution timing measured.',
             'per_episode':episodes}
    return summary,trajectories

def train(kind='robot',timesteps=20000,seed=42,resume=None,scenario_model=None):
    if kind not in ('robot','scenario'): raise ValueError('kind must be robot or scenario')
    if timesteps<256: raise ValueError('At least 256 training timesteps required')
    scenario_policy=PPO.load(scenario_model,device='cpu') if scenario_model else None
    if kind=='scenario':
        factory=ScenarioEnv; model_id='model_3_environment_rl'
    else:
        factory=lambda:SortingEnv(scenario_policy=scenario_policy); model_id='model_4_robotic_rl'
    env=factory(); check_env(env,skip_render_check=True)
    model=PPO.load(resume,env=env,device='cpu') if resume else PPO('MlpPolicy',env,seed=seed,n_steps=256,batch_size=64,verbose=1,device='cpu')
    checkpoints=ROOT/'output/checkpoints'/kind
    callback=CheckpointCallback(save_freq=2048,save_path=str(checkpoints),name_prefix=kind)
    model.learn(total_timesteps=timesteps,callback=callback,reset_num_timesteps=not bool(resume))
    # Evaluation excludes the learned curriculum so all policies face the same held-out distribution.
    eval_factory=ScenarioEnv if kind=='scenario' else SortingEnv
    report,trajectories=evaluate(model,eval_factory)
    if kind=='robot':
        report['rule_baseline']=evaluate(None,SortingEnv,rule=True)[0]
        narrow=PPO('MlpPolicy',SortingEnv(randomized=False),seed=seed,n_steps=256,batch_size=64,verbose=0,device='cpu')
        narrow.learn(total_timesteps=timesteps)
        report['narrow_training_baseline']=evaluate(narrow,SortingEnv)[0]
        report['generalization_difference']=report['completion_rate']-report['narrow_training_baseline']['completion_rate']
    else:
        class RandomPolicy:
            def __init__(self): self.rng=np.random.default_rng(seed)
            def predict(self,obs,deterministic=True): return self.rng.integers(0,10),None
        class RulePolicy:
            def predict(self,obs,deterministic=True): return (4 if obs[0]<.5 else 0),None
        report['random_generator_baseline']=evaluate(RandomPolicy(),ScenarioEnv)[0]
        report['rule_generator_baseline']=evaluate(RulePolicy(),ScenarioEnv)[0]
    folder=ROOT/'output/models'/model_id; folder.mkdir(parents=True,exist_ok=True)
    model.save(folder/'policy.zip')
    finalize(folder,model_id,folder/'policy.zip',{'seed':seed,'additional_timesteps':timesteps,
        'total_timesteps':model.num_timesteps,'algorithm':'PPO','n_steps':256,'batch_size':64,
        'resume':bool(resume),'scenario_model':str(scenario_model) if scenario_model else None,
        'evaluation_seeds':[10000,10049]},report,{'observation':'normalized synthetic features'},'synthetic')
    path=ROOT/'output/datasets/simulation'; path.mkdir(parents=True,exist_ok=True)
    with (path/f'{kind}_evaluation.jsonl').open('w',encoding='utf-8') as f:
        for row in trajectories: f.write(json.dumps(row)+'\n')
    write_json(ROOT/f'output/evaluation/{kind}.json',report)
    return report
