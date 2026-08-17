import socket
import json

class SwarmUDPManager:
    """
    UDP messaging between robots on the same swarm network.

    Used to exchange SCA opinions between robots (rather than the Thymio's
    IR prox_comm, which can only receive one message at a time and cannot
    aggregate several neighbours' opinions per tick).
    """
    def __init__(self, port=5000):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.setblocking(False)

    def send_to_all(self, data_dict, target_ips):
        """
        JSON-encode data_dict and send it to each IP in target_ips on
        this manager's port. Silently skips IPs that fail to send.
        """
        try:
            message = json.dumps(data_dict).encode('utf-8')
            for ip in target_ips:
                try:
                    self.sock.sendto(message, (ip, self.port))
                except Exception as e:
                    pass
        except TypeError:
            print("Error: The data cannot be serialized to JSON.")

    def receive_messages(self):
        """
        Catch all pending UDP messages and return the latest payload per 
        source IP, as {ip: payload}. Using the source IP as key means 
        only the most recent message per neighbour is kept, so a neighbour 
        is never counted twice in a single tick.
        """
        latest = {}
        try:
            while True:
                data, addr = self.sock.recvfrom(1024)
                try:
                    payload = json.loads(data.decode('utf-8'))
                except json.JSONDecodeError:
                    continue  
                latest[addr[0]] = payload 
        except BlockingIOError:
            pass
        return latest
            

    def close(self):
        self.sock.close()