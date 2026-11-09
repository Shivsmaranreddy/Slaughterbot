from dataclasses import dataclass
import math

@dataclass
class SafetyController:
    position: int = 2
    emergency_stop: bool = True
    interlock: bool = False

    def arm_mock(self):
        # Only the in-memory mock is armed here. No hardware serial implementation is exposed.
        self.interlock = True
        self.emergency_stop = False

    def stop(self):
        self.emergency_stop = True

    def execute(self, action, confidence):
        # Hard bounds cannot be relaxed by configuration or a learned policy.
        if self.emergency_stop or not self.interlock:
            return {'accepted':False,'reason':'Safety interlock/stop','position':self.position}
        if type(action) is not int or action not in (0,1,2):
            return {'accepted':False,'reason':'Invalid task action','position':self.position}
        if isinstance(confidence, bool) or not isinstance(confidence, (int,float)) or not math.isfinite(confidence) or not 0.8 <= confidence <= 1:
            return {'accepted':False,'reason':'Insufficient or invalid perception confidence','position':self.position}
        target = self.position + (action - 1)
        if not 0 <= target <= 4:
            return {'accepted':False,'reason':'Movement limit','position':self.position}
        self.position = target
        return {'accepted':True,'position':self.position,'mode':'MOCK_ONLY'}
