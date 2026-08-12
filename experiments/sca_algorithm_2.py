import asyncio
import socket
import os

from behaviours.obstacle_avoidance import ObstacleAvoidance
from behaviours.color_recognition import ColorRecognition
from behaviours.sca_algorithm_2 import SCA 
from swarm_platform.controller.client import SwarmClient
from utils.communication import SwarmUDPManager 

class SCAExperiment:
    """ Implement the SCA algorithm using the Optitrack system to get the position of the robots and their distance to each other."""

    def __init__(self, robot, config=None, logger=None):
        self.robot = robot
        self.logger = logger
        self.config = config or {}

        self.running = True
        self.paused = False

        self.robot_id = socket.gethostname()
        
        coordinator_ip = os.getenv("SWARM_COORDINATOR", "10.15.2.63")
        coordinator_port = int(os.getenv("SWARM_COORDINATOR_PORT", "9100"))
        self.client = SwarmClient(coordinator_ip, coordinator_port)
        self.udp = SwarmUDPManager(port=5000)
        self.target_ips = []
        
        self.wheel_velocity = self.config.get("wheel_velocity", 200)

        self.obstacle_avoidance = ObstacleAvoidance(wheel_velocity=self.wheel_velocity)
        self.color_recognition = ColorRecognition()
        self.sca_algorithm = SCA()

        self.radius = 0.5
        self.max_prox = 800

        self.tick = 0

    async def refresh_peers(self):
        robots = await self.client.list_robots()
        self.target_ips = [
            info["ip"] for rid, info in robots.items() if rid != self.robot_id
        ]
        print(f"[PEERS] {self.target_ips}")

    async def run(self):
        await self.refresh_peers()

        while self.running:

            if self.paused:
                await self.robot.stop()
                await asyncio.sleep(0.05)
                continue

            prox = await self.robot.proximity_horizontal()
            left, right = self.obstacle_avoidance.step_motion(prox)
            
            ground = await self.robot.proximity_ground_reflected()
            patch, _ = self.color_recognition.filtered_color(ground)

            nearby_hostnames = await self.robot.get_neighbours(self.radius)
            relative_poses = await self.robot.get_relative_poses(nearby_hostnames)

            received = self.udp.receive_messages()

            neighbours = {}
            for id, msg in received.items():
                if msg.get("id") in relative_poses:
                    rel = relative_poses[msg.get("id")]
                    msg["distance"] = rel.distance
                    msg["bearing"] = rel.bearing
                    neighbours[id] = msg
             
            left_bias, right_bias, opinion, quality, rarity, authority, buffer = self.sca_algorithm.sca_tick(patch, neighbours)

            if max(prox[:5]) < self.max_prox :
                left += left_bias
                right += right_bias

            self.udp.send_to_all(
                {"id": self.robot_id, 
                 "tick": self.tick,  
                 "opinion": opinion, 
                 "quality": quality, 
                 "authority": authority}, 
                self.target_ips
            )
            
            await self.robot.drive(left, right)

            if self.logger:
                self.logger.log(
                    state={"proximity": prox,
                           "reflected": ground},
                    command={
                        "left_motor": left,
                        "right_motor": right,
                        "patch": patch,
                        "opinion": opinion,
                        "quality": quality,
                        "rarity": rarity,
                        "authority": authority,
                        "buffer": buffer
                    },
                )

            await asyncio.sleep(0.05)
            self.tick += 1
        await self.robot.stop()


    async def pause(self):
        self.paused = True

    async def resume(self):
        self.paused = False

    async def stop(self):
        self.running = False