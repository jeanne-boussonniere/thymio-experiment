import asyncio
import os
import socket
 
from swarm_platform.controller.client import SwarmClient
from utils.communication import SwarmUDPManager 
 
 
class MessagingTestExperiment:
 
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
                await asyncio.sleep(0.05)
                continue
 
            self.udp.send_to_all(
                {"robot_id": self.robot_id, "tick": self.tick},
                self.target_ips,
            )
 
            received = self.udp.receive_messages()

            if self.logger:
                self.logger.log(
                state={"message":received},
                            )
 
            self.tick += 1
            await asyncio.sleep(1)
 
        self.udp.close()
 
    async def pause(self):
        self.paused = True
 
    async def resume(self):
        self.paused = False
 
    async def stop(self):
        self.running = False