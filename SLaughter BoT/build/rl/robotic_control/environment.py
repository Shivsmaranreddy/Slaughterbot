import gymnasium as gym
from gymnasium import spaces
import numpy as np
from build.hardware.controller import SafetyController

class SortingEnv(gym.Env):
    """Five-position inert-object positioning simulator; features are synthetic, not camera detections."""
    metadata={'render_modes':[]}
    def __init__(self,randomized=True,scenario_policy=None):
        self.action_space=spaces.Discrete(3)  # left, hold, right
        self.observation_space=spaces.Box(0,1,(7,),dtype=np.float32)
        self.randomized=randomized; self.scenario_policy=scenario_policy; self.done=True
    def _obs(self):
        return np.array([self.controller.position/4,self.target/4,self.category,self.confidence,
                         self.steps/20,float(self.controller.emergency_stop),self.disturbance],dtype=np.float32)
    def reset(self,seed=None,options=None):
        super().reset(seed=seed)
        self.controller=SafetyController(); self.controller.arm_mock()
        self.target=int(self.np_random.integers(0,5)) if self.randomized else 4
        self.category=int(self.np_random.integers(0,2)); self.steps=0
        self.confidence=float(self.np_random.uniform(.75,1)) if self.randomized else 1.
        self.disturbance=float(self.np_random.uniform(0,.2)) if self.randomized else 0.
        if self.scenario_policy is not None:
            action,_=self.scenario_policy.predict(np.array([0.5,0.5],dtype=np.float32),deterministic=False)
            self.target=int(action)%5
            self.disturbance=0.15 if int(action)>=5 else 0.
        self.done=False
        return self._obs(),{'provenance':'synthetic','seed':seed}
    def step(self,action):
        if self.done: raise RuntimeError('Call reset before step')
        if not self.action_space.contains(action): raise ValueError('Invalid action')
        if self.np_random.random()<self.disturbance: self.confidence=.7
        result=self.controller.execute(int(action),self.confidence)
        self.steps+=1
        success=result['accepted'] and self.controller.position==self.target
        reward=5. if success else -.1 if result['accepted'] else -.5
        terminated=bool(success); truncated=self.steps>=20 and not terminated
        self.done=terminated or truncated
        info={'success':bool(success),'invalid_action':not result['accepted'],
              'safety_violation':not 0<=self.controller.position<=4,'provenance':'synthetic'}
        self.confidence=float(self.np_random.uniform(.8,1))
        return self._obs(),reward,terminated,truncated,info

def rule_action(obs):
    return 2 if obs[1]>obs[0] else 0 if obs[1]<obs[0] else 1
