import gymnasium as gym
from gymnasium import spaces
import numpy as np
from build.rl.robotic_control.environment import SortingEnv, rule_action

class ScenarioEnv(gym.Env):
    """A contextual one-step curriculum bandit. Learned only after PPO training.

    Ten choices select a target and disturbance tier. Reward prefers challenging, still
    solvable scenarios against a frozen rule controller. This is not learned physics.
    """
    metadata={'render_modes':[]}
    def __init__(self):
        self.observation_space=spaces.Box(0,1,(2,),dtype=np.float32)
        self.action_space=spaces.Discrete(10); self.done=True
    def reset(self,seed=None,options=None):
        super().reset(seed=seed); self.done=False
        self.obs=self.np_random.uniform(0,1,2).astype(np.float32)
        return self.obs.copy(),{'provenance':'synthetic'}
    def step(self,action):
        if self.done: raise RuntimeError('Call reset before step')
        if not self.action_space.contains(action): raise ValueError('Invalid scenario')
        env=SortingEnv(); obs,_=env.reset(seed=int(self.np_random.integers(0,2**31-1)))
        env.target=int(action)%5; env.disturbance=.15 if action>=5 else 0.
        env.controller.position=int(self.obs[0]*5); obs=env._obs()
        count=0; failures=0; success=False
        for _ in range(20):
            obs,_,term,trunc,info=env.step(rule_action(obs)); count+=1; failures+=info['invalid_action']
            if term or trunc: success=info['success']; break
        challenge=count/20
        reward=1.-abs(challenge-float(self.obs[1])) if success else -1.
        self.done=True
        return self.obs.copy(),float(reward),True,False,{'success':success,'steps':count,
            'invalid_actions':failures,'scenario':int(action),'provenance':'synthetic'}
