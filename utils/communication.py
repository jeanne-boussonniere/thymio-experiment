import socket
import json

class SwarmUDPManager:
    def __init__(self, port=5000):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.setblocking(False)

    def send_to_all(self, data_dict, target_ips):
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