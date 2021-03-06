import socket
import time
import logging
import sys


class MyServer:
    """
    Class for the server instance
    """
    TCP_PORT = 9870
    BUFFER_SIZE = 1024
    TIMEOUT = 0.2

    def __init__(self):
        """
        Constructor of the class
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4, TCP socket
        self.socket.bind(('', self.TCP_PORT)) #the socket is reachable by any address the machine happens to have
        self.socket.listen(5)
        self.socket.settimeout(0.1)
        self.heartbeats = {}  # dict where key:address, value:heartbeats
        self.timestamps = {}  # dict where key:address, value:timestamp

        logging.basicConfig(stream=sys.stdout, format='%(levelname)s - %(asctime)s - %(message)s',
                            level=logging.INFO)  #logging.INFO is futile, still won't appear on journalctl (warn or >)

        logging.warning("Init successful!")

    def start(self):
        """
        Function that listens for clients and checks for disconnections
        :return: None
        """
        while 1:
            try:
                self.set_connection()
            except socket.timeout:
                pass

            self.check_alive()

    def set_connection(self):
        """
        Function that keeps track of the clients that are connected
        :return: None
        """
        clientsocket, addressport = self.socket.accept()
        logging.warning(f"Connection from {addressport[0]} has been established")
        clientsocket.settimeout(self.TIMEOUT)
        address = addressport[0]

        if address not in self.timestamps:
            self.timestamps[address] = time.time()
            #logging.warning(f"First connection of {address}")

        #logging.warning(f"Dict keys: {self.timestamps.keys()}")

        while 1:
            message = self.read_buffer(connection=clientsocket)

            if not message:
                break

            heartbeat = message.decode("utf-8")
            self.check_reconnected(heartbeat=heartbeat, address=address)
            self.heartbeats[address] = heartbeat
            logging.warning(f"Heartbeat --> {heartbeat} RECEIVED from address --> {address}")

        clientsocket.close()

    def read_buffer(self, connection):
        """
        Function that reads the message from the client
        :param connection: the connection to the server
        :return: heartbeat
        """
        data = None

        try:
            data = connection.recv(self.BUFFER_SIZE)
        except socket.timeout:
            logging.exception("Exception occurred: SOCKET TIMEOUT")

        return data

    def check_reconnected(self, heartbeat, address):
        """
        Function that checks if a client has reconnected after a crash, it updates the heartbeats dict
        :param heartbeat: If the address reconnected, the received heartbeat will begin from 0 again.
        :param address: The address that is checked
        :return: None
        """
        try:
            if self.heartbeats[address] > heartbeat:
                self.timestamps[address] = time.time()
                self.heartbeats[address] = heartbeat
                logging.critical(f"RECONNECTED {address}")
        except KeyError:
            logging.exception("Exception occured: KEY ERROR!")

    def check_alive(self):
        """
        Function that checks for the disconnected clients
        :return: None
        """

        for address, heartbeats in self.heartbeats.items():
            if address == "127.0.0.1":
                continue
            else:
                time_diff = time.time() - self.timestamps[address]
                treshold = 1

                if time_diff > (int(heartbeats) + treshold):
                    logging.critical(f"CLIENT {address} DISCONNECTED! time: {time_diff} ; heartbeats: {heartbeats}")


if __name__ == "__main__":
    srv = MyServer()
    srv.start()
