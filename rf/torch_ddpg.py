'''
torch = 0.41
'''
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import time
from tensorboardX import SummaryWriter


###############################  DDPG  ####################################

class ANet(nn.Module):   # ae(s)=a

    def __init__(self, s_dim, a_dim, a_bound, N_BLOCKS=5):
        super(ANet,self).__init__()

        self.a_bound = a_bound
        self.N_BLOCKS = N_BLOCKS
        self.s_dim = s_dim

        self.CNN_1 = nn.Conv1d(1, 1, 2)
        self.CNN_fc_1 = nn.Linear(N_BLOCKS-1, 1)
        self.CNN_fc_1.weight.data.normal_(0, 0.1)

        self.CNN_2 = nn.Conv1d(1, 1, 2)
        self.CNN_fc_2 = nn.Linear(N_BLOCKS - 1, 1)
        self.CNN_fc_2.weight.data.normal_(0, 0.1)

        self.CNN_3 = nn.Conv1d(1, 1, 2)
        self.CNN_fc_3 = nn.Linear(N_BLOCKS - 1, 1)
        self.CNN_fc_3.weight.data.normal_(0, 0.1)

        self.fc1 = nn.Linear(s_dim, 30)
        self.fc1.weight.data.normal_(0, 0.1) # initialization
        self.out = nn.Linear(30, a_dim)
        self.out.weight.data.normal_(0, 0.1) # initialization


    def forward(self, x):

        x_ = torch.FloatTensor(np.zeros((x.shape[0], self.s_dim)))
        x = torch.FloatTensor(x)
        x_[:, :3] = x[:, :3]

        x_[:, 3] = nn.ReLU()(
            self.CNN_fc_1(
                self.CNN_1(x[:, 3 + 0*self.N_BLOCKS: 3 + (0+1)*self.N_BLOCKS].reshape((-1, 1, self.N_BLOCKS))
            ))).reshape((-1))

        x_[:, 4] = nn.ReLU()(
            self.CNN_fc_2(
                self.CNN_2(x[:, 3 + 1 * self.N_BLOCKS: 3 + (1 + 1) * self.N_BLOCKS].reshape((-1, 1, self.N_BLOCKS))
                           ))).reshape((-1))

        x_[:, 5] = nn.ReLU()(
            self.CNN_fc_3(
                self.CNN_3(x[:, 3 + 2 * self.N_BLOCKS: 3 + (2 + 1) * self.N_BLOCKS].reshape((-1, 1, self.N_BLOCKS))
                           ))).reshape((-1))

        x_ = self.fc1(x_)
        x_ = F.relu(x_)
        x_ = self.out(x_)
        x_ = F.softmax(x_, 1)
        actions_value = x_*self.a_bound

        return actions_value


class CNet(nn.Module):   # ae(s)=a

    def __init__(self, s_dim, a_dim, N_BLOCKS=5):
        super(CNet,self).__init__()

        self.N_BLOCKS = N_BLOCKS
        self.s_dim = s_dim

        self.CNN_1 = nn.Conv1d(1, 1, 2)
        self.CNN_fc_1 = nn.Linear(N_BLOCKS - 1, 1)
        self.CNN_fc_1.weight.data.normal_(0, 0.1)

        self.CNN_2 = nn.Conv1d(1, 1, 2)
        self.CNN_fc_2 = nn.Linear(N_BLOCKS - 1, 1)
        self.CNN_fc_2.weight.data.normal_(0, 0.1)

        self.CNN_3 = nn.Conv1d(1, 1, 2)
        self.CNN_fc_3 = nn.Linear(N_BLOCKS - 1, 1)
        self.CNN_fc_3.weight.data.normal_(0, 0.1)

        self.fcs = nn.Linear(s_dim, 30)
        self.fcs.weight.data.normal_(0, 0.1) # initialization
        self.fca = nn.Linear(a_dim, 30)
        self.fca.weight.data.normal_(0, 0.1) # initialization
        self.out = nn.Linear(30, 1)
        self.out.weight.data.normal_(0, 0.1)  # initialization


    def forward(self, s, a):

        x_ = torch.FloatTensor(np.zeros((s.shape[0], self.s_dim)))
        s = torch.FloatTensor(s)
        x_[:, 3] = s[:, 3]

        x_[:, 3] = nn.ReLU()(
            self.CNN_fc_1(
                self.CNN_1(s[:, 3 + 0 * self.N_BLOCKS: 3 + (0 + 1) * self.N_BLOCKS].reshape((-1, 1, self.N_BLOCKS))
                           ))).reshape((-1))

        x_[:, 4] = nn.ReLU()(
            self.CNN_fc_2(
                self.CNN_2(s[:, 3 + 1 * self.N_BLOCKS: 3 + (1 + 1) * self.N_BLOCKS].reshape((-1, 1, self.N_BLOCKS))
                           ))).reshape((-1))

        x_[:, 5] = nn.ReLU()(
            self.CNN_fc_3(
                self.CNN_3(s[:, 3 + 2 * self.N_BLOCKS: 3 + (2 + 1) * self.N_BLOCKS].reshape((-1, 1, self.N_BLOCKS))
                           ))).reshape((-1))

        x = self.fcs(x_)
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
                 TAU,
                 N_BLOCKS
                 ):
        self.a_dim, self.s_dim, self.a_bound = a_dim, s_dim, a_bound,

        self.MEMORY_CAPACITY = memory_capacity
        self.BATCH_SIZE = batch_size
        self.TAU = TAU
        self.LR_A, self.LR_C, self.GAMMA = lr_a, lr_c, gamma
        self.N_BLOCKS = N_BLOCKS

        self.MEM_S_DIM = (3 + 3*N_BLOCKS) * 2 + a_dim + 1
        self.memory = np.zeros((self.MEMORY_CAPACITY, self.MEM_S_DIM), dtype=np.float32)
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

        indices = np.random.choice(self.MEMORY_CAPACITY, size=self.BATCH_SIZE)
        b_t = self.memory[indices, :]
        b_s = b_t[:, :3+3*self.N_BLOCKS]
        b_a = torch.FloatTensor(b_t[:, 3+3*self.N_BLOCKS: 3+3*self.N_BLOCKS + self.a_dim])
        b_r = torch.FloatTensor(b_t[:, -(3+3*self.N_BLOCKS) - 1])
        b_s_ = b_t[:, -(3+3*self.N_BLOCKS):]

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
        transition = s+a+r+s_
        index = self.pointer % self.MEMORY_CAPACITY  # replace the old memory with new memory
        # print(transition)
        self.memory[index] = transition
        self.pointer += 1


    def save2onnx(self, file_name=None):

        # 使用时间戳命名onnx文件
        if not file_name:
            file_name ='output/torch_%s_suffix.onnx' % ''.join(str(time.time()).split('.'))

        # b_s = torch.FloatTensor(self.memory[:2, :3+3*self.N_BLOCKS]).reshape((-1, 3+3*self.N_BLOCKS)).detach()
        b_s = torch.autograd.Variable(torch.FloatTensor(self.memory[0, -(3+3*self.N_BLOCKS):].reshape((-1, 3+3*self.N_BLOCKS))), requires_grad=False)
        b_s_ = torch.autograd.Variable(torch.FloatTensor(self.memory[0, -(3+3*self.N_BLOCKS):].reshape((-1, 3+3*self.N_BLOCKS))), requires_grad=False)

        # with SummaryWriter(comment='Actor_eval') as w:
        #     w.add_graph(self.Actor_eval, (b_s,))
        #     # w.add_graph(self.Critic_eval, (b_s,))

        output = torch.onnx.export(self.Actor_eval,
                                   b_s,
                                   file_name.replace('suffix', 'eval'),
                                   verbose=True)

        output = torch.onnx.export(self.Actor_target,
                                   b_s_,
                                   file_name.replace('suffix', 'target'),
                                   verbose=True)

        return file_name.replace('suffix', 'eval')


    def load_onnx(self, file_name='output/torch_15728833105783641_eval.onnx'):

        if not file_name:
            return None
        import onnx
        # import onnx_caffe2.backend as backend
        import caffe2.python.onnx.backend as backend
        print("load_onnx")
        model = onnx.load(file_name)

        rep = backend.prepare(model, device='CPU')
        s = np.array([0.15464788732394366, 0.497, 0.0, 0.9992660479428109, 0.0, 0.567515], dtype=np.float32).reshape((-1, self.s_dim))

        print(rep.run(s))
        print(self.choose_action([0.15464788732394366, 0.497, 0.0, 0.9992660479428109, 0.0, 0.567515]))