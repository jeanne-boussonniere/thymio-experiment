class ObstacleAvoidance:

    def __init__(
        self,
        wheel_velocity=200,
    ):
        self.wheel_velocity = wheel_velocity

        self.count_backward = 0
        self.count_turn = 0
        self.max_backward = 10
        self.min_turn = 5
        self.max_turn = 35
        self.backward = False
        self.max_prox_center = 2000
        self.max_prox_side = 800
        self.turn_direction = None


    def step_motion(self, prox):
        left = prox[0] + prox[1]
        right = prox[3] + prox[4]
        closer = max(prox[:5])
        if not self.backward: 
            if prox[2] >= self.max_prox_center or (left >= self.max_prox_center and right >= self.max_prox_center):
                self.backward = True
                self.turn_direction = None
                self.count_turn = 0
                return -self.wheel_velocity, -self.wheel_velocity
            elif closer >= self.max_prox_side:
                if self.turn_direction is not None and self.count_turn < self.max_turn:
                    self.count_turn += 1
                    if self.turn_direction == "right" and (right - left) > 400:
                        self.turn_direction = "left"
                    elif self.turn_direction == "left" and (left - right) > 400:
                        self.turn_direction = "right"

                    if self.turn_direction == "right":
                        factor = self._factor(closer)
                        return self.wheel_velocity, self.wheel_velocity * max(0, 1 - 2 * factor)
                    else:
                        factor = self._factor(closer)
                        return self.wheel_velocity * max(0, 1 - 2 * factor), self.wheel_velocity
                elif self.turn_direction is not None and self.count_turn >= self.max_turn:
                    self.backward = True
                    self.turn_direction = None
                    self.count_turn = 0
                    return -self.wheel_velocity, -self.wheel_velocity
                else:
                    self.count_turn = 0
                    if left > right:
                        factor = self._factor(closer)
                        self.turn_direction = "right"
                        return self.wheel_velocity, self.wheel_velocity * max(0, 1 - 2 * factor)
                    else:
                        factor = self._factor(closer)
                        self.turn_direction = "left"
                        return self.wheel_velocity * max(0, 1 - 2 * factor), self.wheel_velocity
            elif self.turn_direction is not None and self.count_turn < self.min_turn:
                self.count_turn += 1
                if self.turn_direction == "right":
                    factor = self._factor(closer)
                    return self.wheel_velocity, self.wheel_velocity * max(0, 1 - 2 * factor)
                else:
                    factor = self._factor(closer)
                    return self.wheel_velocity * max(0, 1 - 2 * factor), self.wheel_velocity
            else:  
                self.turn_direction = None
                self.count_turn = 0
                return self.wheel_velocity, self.wheel_velocity
        else:
            self.count_backward += 1
            if self.count_backward < self.max_backward and prox[5] < self.max_prox_side and prox[6] < self.max_prox_side:
                return -self.wheel_velocity, -self.wheel_velocity
            elif self.count_backward < self.max_backward and (prox[5] >= self.max_prox_side or prox[6] >= self.max_prox_side):
                self.count_backward = self.max_backward
                if left > right:
                    return self.wheel_velocity, -self.wheel_velocity
                else:
                    return -self.wheel_velocity, self.wheel_velocity
            elif self.count_backward >= self.max_backward and self.count_backward < (self.max_backward + 5):
                if left > right:
                    return self.wheel_velocity, -self.wheel_velocity
                else:
                    return -self.wheel_velocity, self.wheel_velocity
            else:
                self.count_backward = 0
                self.backward = False
                return self.wheel_velocity, self.wheel_velocity

    def _factor(self, closer):
        factor = (closer - self.max_prox_side) / (4500 - self.max_prox_side)
        return max(0.0, min(1.0, factor))