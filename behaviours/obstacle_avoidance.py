class ObstacleAvoidance:

    def __init__(
        self,
        wheel_velocity=200,
    ):
        self.wheel_velocity = wheel_velocity

        self.count_backward = 0
        self.count_turn = 0
        self.max_backward = 10
        self.max_turn = 10
        self.backward = False
        self.max_prox_center = 3500
        self.max_prox_side = 1500
        self.turn_direction = None


    def step_motion(self, prox):
        left = prox[0] + prox[1]
        right = prox[3] + prox[4]
        if not self.backward: 
            if prox[2] >= self.max_prox_center :
                self.backward = True
                self.turn_direction = None
                return -self.wheel_velocity, -self.wheel_velocity
            elif prox[1] >= self.max_prox_center and prox[3] >= self.max_prox_center:
                self.backward = True
                self.turn_direction = None
                return -self.wheel_velocity, -self.wheel_velocity
            elif prox[0] >= self.max_prox_side or prox[1] >= self.max_prox_side or prox[3] >= self.max_prox_side or prox[4] >= self.max_prox_side:
                if self.turn_direction is not None and self.count_turn < self.max_turn:
                    self.count_turn += 1
                    if self.turn_direction == "right":
                        return self.wheel_velocity, -self.wheel_velocity
                    else:
                        return -self.wheel_velocity, self.wheel_velocity
                else:
                    self.count_turn = 0
                    if left > right:
                        self.turn_direction = "right"
                        return self.wheel_velocity, -self.wheel_velocity
                    else:
                        self.turn_direction = "left"
                        return -self.wheel_velocity, self.wheel_velocity
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

             