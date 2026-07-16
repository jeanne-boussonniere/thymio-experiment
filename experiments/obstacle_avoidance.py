import asyncio
import math

from behaviours.obstacle_avoidance import ObstacleAvoidance
# from utils.geometry import SENSOR_ANGLES

class ObstacleAvoidanceExperiment:

    def __init__(self, robot, config=None, logger=None):
        self.robot = robot
        self.logger = logger
        self.config = config or {}

        self.running = True
        self.paused = False

        # Parameters
        self.wheel_velocity = self.config.get("wheel_velocity", 100)

        self.turning_left = 0

        self.obstacle_avoidance = ObstacleAvoidance(wheel_velocity=self.wheel_velocity)

        # Approximate Thymio proximity sensor angles (radians)
        # self.sensor_angles = SENSOR_ANGLES

    async def run(self):

        while self.running:

            if self.paused:
                await self.robot.stop()
                await asyncio.sleep(0.05)
                continue

            prox = await self.robot.proximity_horizontal()

            left, right = self.obstacle_avoidance.step_motion(prox)

            await self.robot.drive(left, right)

            if self.logger:
                self.logger.log(
                    state={"proximity": prox},
                    command={
                        "left_motor": left,
                        "right_motor": right,
                    },
                )

            await asyncio.sleep(0.05)

        await self.robot.stop()


    async def pause(self):
        self.paused = True

    async def resume(self):
        self.paused = False

    async def stop(self):
        self.running = False