import socket
import sys
import time
import threading
import logging

class MyClient:
    TCP_PORT = 9870
    BUFFER_SIZE = 1024

    def __init__(self):
        """
        Constructor of the class.
        """
        self.heartbeat_counter = {}  # remember the heartbeat counter for each server in the server list separately
        file = open(sys.argv[1], 'r')
        self.server_list = [line.strip() for line in file.readlines()]

        for server in self.server_list:
            self.heartbeat_counter[server] = 0

        logging.basicConfig(stream=sys.stdout, format='%(levelname)s - %(asctime)s - %(message)s')
        logging.warning(f"Reading server.txt succeded! Content: {self.server_list}")

    def start(self):
        self.connect()

        while 1:
            time.sleep(100)

    def connect(self):
        """
        Connects to the servers from the argument list and sends the heartbeat. if the client has reconnected
        the heartbeat starts from 0 again
        :return: None
        """
        t = threading.Timer(1, self.connect)
        t.start()

        for server in self.server_list:
            logging.warning(f"Connecting to {server}")

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((server, self.TCP_PORT))
                s.send(bytes(str(self.heartbeat_counter[server]), "utf-8"))
                s.close()
                self.heartbeat_counter[server] += 1
                logging.warning(f"Heartbeat {self.heartbeat_counter[server]} SENT")
            except ConnectionRefusedError:
                self.heartbeat_counter[server] = 0
                logging.warning("Exception occured!")


if __name__=="__main__":
    c = MyClient()
    c.start()