import random
import math

class SCA :
    PATCHES = [
        {"index": 0, "quality": 0.30, "name": "black"},  
        {"index": 1, "quality": 0.60, "name": "white"},  
        {"index": 2, "quality": 0.90, "name": "brown"}   
    ]
    COLOR_EPS = 20
    NOISE_SIGMA = 0.05
    OMEGA_POS = 0.8
    ETA_ADOPT = 0.35
    W = 15
    BETA_Q = 0.3
    BETA_RHO = 0.3
    AUTHORITY_THRESHOLD = 0.5
    TAU_Q = 0.40
    CASCADE_DECAY = 0.08
    ADOPTION_MARGIN = 0.2
    SPEED = 200

    def __init__(
        self
    ):
        self.patch = -1
        self.opinion = -1
        self.quality = 0.0
        self.rho = 0.0
        self.authority = 0.0
        self.kappa = 0
        self.cascade_active = False
        self.buffer = {}
        self.tick = 0
        

    def sca_tick(self, patch, neighbours):
        self.tick += 1
        self.patch = patch

        # Step 1 - detect patch & measure quality
        if patch != -1 :
            if self.opinion == -1:
                self.opinion = patch
            if self.opinion == patch:
                self.quality = self._measure_quality(patch)

        #Step 2 - compute rarity
        self._update_buffer(neighbours)
        self.rho = self._compute_rarity()

        # Step 3 - update authority & cascade
        if self.rho >= self.AUTHORITY_THRESHOLD and self.quality > self.TAU_Q:
            if not self.cascade_active:
                self.kappa = 0
                self.cascade_active = True
            self.authority = self._calculate_authority()
            self.kappa += 1
        elif self.cascade_active and self.patch != -1:
            self.authority = self._calculate_authority()
            self.kappa += 1
        else:
            self.authority = 0.0
            self.cascade_active = False

        left_bias, right_bias = self._measure_bias(neighbours)
        
        self._change_opinion(neighbours)

        return left_bias, right_bias, self.opinion, self.quality, self.rho, self.authority, self.buffer

    
    def _measure_quality(self, patch):
        true_q = self.PATCHES[patch]["quality"]
        q_raw = random.gauss(true_q, self.NOISE_SIGMA)
        return self.BETA_Q*q_raw + (1-self.BETA_Q)*self.quality
    
    def _update_buffer(self, neighbours):
        for n in neighbours.values() : 
            self.buffer[n["id"]] = {"opinion":n["opinion"],"last_seen":self.tick}
        delete = []
        for i,a in self.buffer.items() : 
            if self.tick - self.W > a["last_seen"] :
                delete.append(i)
        for id in delete : 
            del self.buffer[id]

    def _compute_rarity(self):
        n = len(self.buffer)
        s = 0
        for a in self.buffer.values() : 
            if self.opinion == a["opinion"] : 
                s += 1
        if self.opinion == -1 or self.patch == -1:
            return 0.0
        elif n == 0 : 
            return self.rho
        else : 
            return self.BETA_RHO*(1-s/n)+(1-self.BETA_RHO)*self.rho
        
    def _calculate_authority(self):
        if self.quality <= 0.0 : 
            return 0.0
        g = max(0,(self.quality-self.TAU_Q)/(1-self.TAU_Q))
        return self.rho * g * math.exp(-self.CASCADE_DECAY/self.quality * self.kappa)

    def _change_opinion(self,neighbours):
        max_A = 0
        new_opinion = None
        quality_n = 0
        for n in neighbours.values():
            if n["authority"] > max_A : 
                max_A = n["authority"]
                new_opinion = n["opinion"]
                quality_n = n["quality"]
        if max_A > 0 and max_A > self.authority*(1 + self.ADOPTION_MARGIN) and new_opinion != self.opinion and quality_n > self.quality :
            self.opinion = new_opinion
            self.cascade_active = False
            self.kappa = 0
            self.authority = 0.0
            self.quality = quality_n

    def _measure_bias(self, neighbours):
        sum_x, sum_y = 0.0, 0.0
        for n in neighbours.values():
            if n["authority"] <= 0.0:
                continue
            distance = n.get("distance")
            bearing = n.get("bearing")
            if distance is None or bearing is None:
                continue

            weight = n["authority"] * math.exp(-self.OMEGA_POS * distance)
            sum_x += weight * math.cos(bearing)
            sum_y += weight * math.sin(bearing)

        norm = math.hypot(sum_x, sum_y)
        if norm > 0:
            dir_x, dir_y = sum_x / norm, sum_y / norm
        else:
            dir_x, dir_y = 0.0, 0.0

        bx = self.ETA_ADOPT * dir_x
        by = self.ETA_ADOPT * dir_y

        angle = math.atan2(by, bx)  
        turn_strength = min(abs(angle) / math.pi, 1.0)
        extra = turn_strength * 0.5 * self.SPEED 

        if angle > 0:
            left_bias, right_bias = -extra, extra
        else:
            left_bias, right_bias = extra, -extra

        return left_bias, right_bias

