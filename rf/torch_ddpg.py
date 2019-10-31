'''
torch = 0.41
'''
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import time


###############################  DDPG  ####################################

class ANet(nn.Module):   # ae(s)=a

    def __init__(self,s_dim, a_dim, a_bound):
        super(ANet,self).__init__()

        self.a_bound = a_bound

        self.fc1 = nn.Linear(s_dim, 30)
        self.fc1.weight.data.normal_(0, 0.1) # initialization
        self.out = nn.Linear(30, a_dim)
        self.out.weight.data.normal_(0, 0.1) # initialization


    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        x = self.out(x)
        x = F.softmax(x, 1)
        actions_value = x*self.a_bound

        return actions_value


class CNet(nn.Module):   # ae(s)=a

    def __init__(self, s_dim, a_dim):
        super(CNet,self).__init__()
        self.fcs = nn.Linear(s_dim, 30)
        self.fcs.weight.data.normal_(0, 0.1) # initialization
        self.fca = nn.Linear(a_dim, 30)
        self.fca.weight.data.normal_(0, 0.1) # initialization
        self.out = nn.Linear(30, 1)
        self.out.weight.data.normal_(0, 0.1)  # initialization


    def forward(self, s, a):
        x = self.fcs(s)
        y = self.fca(a)
        net = F.relu(x+y)
        actions_value = self.out(net)

        return actions_value


class DDPG(object):

    def __init__(self,
                 a_dim,
                 s_dim,
                 a_bound,
                 memory_capacity,
                 lr_a,
                 lr_c,
                 gamma,
                 batch_size,
                 TAU
                 ):
        self.a_dim, self.s_dim, self.a_bound = a_dim, s_dim, a_bound,

        self.MEMORY_CAPACITY = memory_capacity
        self.BATCH_SIZE = batch_size
        self.TAU = TAU
        self.LR_A, self.LR_C, self.GAMMA = lr_a, lr_c, gamma

        self.memory = np.zeros((self.MEMORY_CAPACITY, s_dim * 2 + a_dim + 1), dtype=np.float32)
        self.pointer = 0

        self.Actor_eval = ANet(s_dim, a_dim, a_bound)
        self.Actor_target = ANet(s_dim, a_dim, a_bound)
        self.Critic_eval = CNet(s_dim, a_dim)
        self.Critic_target = CNet(s_dim, a_dim)
        self.ctrain = torch.optim.Adam(self.Critic_eval.parameters(), lr=self.LR_C)
        self.atrain = torch.optim.Adam(self.Actor_eval.parameters(), lr=self.LR_A)
        self.loss_td = nn.MSELoss()


    def choose_action(self, s):
        s = torch.unsqueeze(torch.FloatTensor(s), 0)
        return self.Actor_eval(s)[0].detach() # ae（s）


    def learn(self):

        for x in self.Actor_target.state_dict().keys():
            eval('self.Actor_target.' + x + '.data.mul_((1-self.TAU))')
            eval('self.Actor_target.' + x + '.data.add_(self.TAU*self.Actor_eval.' + x + '.data)')
        for x in self.Critic_target.state_dict().keys():
            eval('self.Critic_target.' + x + '.data.mul_((1-self.TAU))')
            eval('self.Critic_target.' + x + '.data.add_(self.TAU*self.Critic_eval.' + x + '.data)')

        # soft target replacement
        #self.sess.run(self.soft_replace)  # 用ae、ce更新at，ct

        indices = np.random.choice(self.MEMORY_CAPACITY, size=self.BATCH_SIZE)
        b_t = self.memory[indices, :]
        b_s = torch.FloatTensor(b_t[:, :self.s_dim])
        b_a = torch.FloatTensor(b_t[:, self.s_dim: self.s_dim + self.a_dim])
        b_r = torch.FloatTensor(b_t[:, -self.s_dim - 1: -self.s_dim])
        b_s_ = torch.FloatTensor(b_t[:, -self.s_dim:])

        a = self.Actor_eval(b_s)
        q = self.Critic_eval(b_s, a)  # loss=-q=-ce（s,ae（s））更新ae   ae（s）=a   ae（s_）=a_
        # 如果 a是一个正确的行为的话，那么它的Q应该更贴近0
        loss_a = -torch.mean(q) 
        #print(q)
        #print(loss_a)
        self.atrain.zero_grad()
        loss_a.backward()
        self.atrain.step()

        a_ = self.Actor_target(b_s_)  # 这个网络不及时更新参数, 用于预测 Critic 的 Q_target 中的 action
        q_ = self.Critic_target(b_s_, a_)  # 这个网络不及时更新参数, 用于给出 Actor 更新参数时的 Gradient ascent 强度
        q_target = b_r+self.GAMMA*q_  # q_target = 负的
        #print(q_target)
        q_v = self.Critic_eval(b_s, b_a)
        #print(q_v)
        td_error = self.loss_td(q_target, q_v)
        # td_error=R + GAMMA * ct（bs_,at(bs_)）-ce(s,ba) 更新ce ,但这个ae(s)是记忆中的ba，让ce得出的Q靠近Q_target,让评价更准确
        #print(td_error)
        self.ctrain.zero_grad()
        td_error.backward()
        self.ctrain.step()


    def store_transition(self, s, a, r, s_):
        transition = np.hstack((s, a, [r], s_))
        index = self.pointer % self.MEMORY_CAPACITY  # replace the old memory with new memory
        self.memory[index, :] = transition
        self.pointer += 1


    def save2onnx(self, file_name=None):

        # 使用时间戳命名onnx文件
        if not file_name:
            file_name ='torch_%s_suffix.onnx' % ''.join(str(time.time()).split('.'))

        # 抽取记忆库中的批数据
        indices = np.random.choice(self.MEMORY_CAPACITY, size=self.BATCH_SIZE)
        b_t = self.memory[indices, :]
        b_s = torch.FloatTensor(b_t[:, :self.s_dim])
        # b_a = torch.FloatTensor(b_t[:, self.s_dim: self.s_dim + self.a_dim])
        # b_r = torch.FloatTensor(b_t[:, -self.s_dim - 1: -self.s_dim])
        b_s_ = torch.FloatTensor(b_t[:, -self.s_dim:])

        output = torch.onnx.export(self.Actor_eval,
                                   b_s,
                                   file_name.replace('suffix', 'eval'),
                                   verbose=False)

        output = torch.onnx.export(self.Actor_target,
                                   b_s_,
                                   file_name.replace('suffix', 'target'),
                                   verbose=False)

        return file_name.replace('suffix', 'target')
