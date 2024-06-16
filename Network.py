import socket
import pickle
import select
import struct
import numpy as np


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.server = "10.0.0.48"
        self.server = "192.168.202.136"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def get_p(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except Exception as e:
            #print("AAAAA", e)
            pass

    def recvall(self, data_size):
        # RECURSION ALGORITHM, IF RETURN NUM CALL GET AGAIN.
        BUFF_SIZE = 1024
        data = []
        while True:
            #socket.setdefaulttimeout(1)
            #read, _, _ = select.select([self.client], [], [])
            #if len(read) == 0:
            #    break
            part = self.client.recv(BUFF_SIZE)
            data.append(part)
            data_size = data_size - len(part)
            if data_size <= 0:
                # either 0 or end of data
                break
        #ata[-1] = data[-1][:len(data[-1]) - len(pickle.dumps("A"))]
        #data.append(pickle.dumps("ub."))
        data = b"".join(data)
        #print(data)
        return data

    def send(self, data):
        self.client.settimeout(1)
        received_data = b""
        self.client.send(pickle.dumps(data))
        data_size = struct.unpack("I", self.client.recv(4))[0]
        #while True:
            #received_data = self.recvall()
            #if received_data != None:
                #break
        #print(received_data)
        #print(data_size)
        # if data_size % 1024 != 0:
        #     for i in range(int(np.ceil(data_size / 1024))):
        #         #print(self.client.recv(2048))
        #         received_data = received_data + self.client.recv(2048)
        #         #print(received_data)
        # else:
        #     for i in range(0, int(np.ceil(data_size / 1024))):
        #         received_data = received_data + self.client.recv(2048)
        #data_received = pickle.loads(self.client.recv(data_size *2))
        #print(pickle.loads(received_data))
        received_data = self.recvall(data_size)
        if received_data == None:
            gmro
        return pickle.loads(received_data)

    def send_without_receive(self, data):
        self.client.send(pickle.dumps(data))
#n = Network()
#print(n.send("Hello, my name is Sol."))
#print(n.send("I enjoy programming!"))