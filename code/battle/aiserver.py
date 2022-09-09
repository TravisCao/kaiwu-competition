import time
import socket
import struct
import json

from framework.common.common_func import log_time_func
from agent import Agent
import numpy as np
def cvt_infer_list_to_numpy_list(infer_list):
    data_list=[]
    for infer in infer_list:
        data_list.append(infer.data)
    return data_list
class AIServer:
    def __init__(self, port,model_cls,model_path):

        self.port = port
        self.sock=None
        # self.model = model_cls()
        self.agent=Agent(model_cls=model_cls,model_pool_addr="",local_mode=True)
        self.agent._predictor.load_model(model_path)
        self.agent.lstm_hidden = np.zeros([self.agent.lstm_unit_size])
        self.agent.lstm_cell = np.zeros([self.agent.lstm_unit_size])
    def prepare_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("0.0.0.0",self.port))
        self.sock.listen(10)
        print("Ai Server start listen at 0.0.0.0:{}".format(self.port))
    def predict(self, input_dict):

        d_action=self.agent.process(input_dict,True)
        for i in range(len(d_action)):
            d_action[i]=int(d_action[i])
        return d_action

    def handle_request(self):
        while True:
            self.env_sock, addr = self.sock.accept()
            print("connect success {}".format(addr), self.env_sock)
            # data = self.env_sock.recv(1024)
            while True:
                log_time_func('recv')
                data = self.env_sock.recv(8192)
                #print("first recv:", end_time - start_time)
                try:
                    while len(data) < 12:

                        l = self.env_sock.recv(8192)
                        if l == b'':
                            raise ConnectionResetError
                        else:
                            data += l
                    pkg_len = struct.unpack("I", data[:4])[0]
                    frame_no = struct.unpack("I", data[4:8])[0]
                    data_len = struct.unpack("I", data[8:12])[0]
                    start_time = time.time()

                    end_time = time.time()
                    log_time_func('recv', end=True)

                    input = json.loads(data[12:data_len + 12].decode("utf-8"))
                    log_time_func('predict')
                    #print("input:",input)
                    d_action = self.predict(input)
                    #print("d_action",d_action)
                    log_time_func('predict', end=True)
                    frame_no_bytes = struct.pack("I", frame_no)
                    data = bytes(json.dumps(d_action).encode("utf-8"))
                    data_len_bytes = struct.pack("I", len(data) + 8)

                    send_data = data_len_bytes + frame_no_bytes + data
                    self.env_sock.send(send_data)
                    data = b''
                    # except:
                    #     print("recv decode failed!")
                except ConnectionResetError:
                    print("connect broken!")
                    break
