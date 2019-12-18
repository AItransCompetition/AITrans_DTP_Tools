import numpy as np
from collections import namedtuple

# reinforcement learning parameters

learning_rate = 0.01
gamma = 0.99
episodes = 20000
render = False
eps = np.finfo(np.float32).eps.item()
SavedAction = namedtuple('SavedAction', ['log_prob', 'value'])

state_space = 12
action_space = 2 * 2


