
import time
import zmq
import json
from user_func import get_action
from user_func import rl_stats
import threading


class Zmq():
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:5555")

    def run(self, states, model):
        
        while True:
            # wait for next request from client
            message = self.socket.recv()

            state = json.loads(message.decode())

            # add new state
            states.append(state)

            
            action = get_action(state, model)
            
            sending_message = str(action[0]) + ',' + str(action[1])
            
            # send reply to client
            self.socket.send(sending_message.encode())


# thread
class Zmq_thread(threading.Thread):
    def __init__(self, threadID, name, states, policy):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.zmq = Zmq()
        self.states = states
        self.policy = policy
    
    def run(self):
        self.zmq.run(self.states, self.policy)