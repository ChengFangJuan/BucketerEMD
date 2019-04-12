# -*- coding:utf-8 -*-
from __future__ import division
import numpy as np

class AgentCFR():

    def __init__(self,name, env, strategy_file_name = None):
        self.name = name
        self.env = env
        self.actions = np.zeros(3)
        self.played = 0
        self.reward = 0
        self.strategy = self.get_strategy(strategy_file_name)


    def get_strategy(self, strategy_file_name):
        strategy = dict()
        strategy_file_name_ = strategy_file_name
        if strategy_file_name is None:
            strategy_file_name_ = "agent/strategy.txt"
        file = open(strategy_file_name_,'r')
        line = file.readline()
        line = line[:-1]
        id = line.split(":")
        strategy_ = id[1][1:-1].split(',')
        strategy[id[0]] = strategy_
        while line:
            line = file.readline()
            line = line[:-1]
            if line == "":
                break
            id = line.split(":")
            strategy_ = id[1][1:-1].split(',')
            strategy[id[0]] = strategy_
        file.close()
        return strategy

    def computer_action(self,state):
        assert state in self.strategy, 'Information not in strategy dict'
        action_ = self.strategy[state]
        action = [0,0,0]
        for i in range(len(action_)):
            action[i]=float(action_[i])
        action = np.array(action)
        action_cum_sum = action.cumsum()
        p = np.random.random(1)
        action_index = None

        for i in range(len(action_cum_sum)):
            if p[0] < action_cum_sum[i]:
                action_index = i
                break
        out = [0,0,0]
        out[action_index] = 1
        return np.array(out)

    def play(self, index, s2=None, batch = None):
        a = None
        if s2 is None:
            s, a, r, ond_state, t, s2 = self.env.get_state(index)
            self.reward += r  # 记录玩家总共累计的输赢值
            if t:
                return t
        else:  # because it's the initial state
            t = False # 游戏是否结束

        if not t:
            a = self.computer_action(s2)
            self.env.step(a, index)
            self.played += 1 # 执行动作的次数

        self.actions[np.argmax(a)] += 1 # 记录每个动作执行的次数
        return t


    def sampled_actions(self):
        print("{} played {} times: Folds: {}, Calls: {}, Raises: {} - Reward: {}".format(self.name,
                                                                                         self.played,
                                                                                         self.actions[0],
                                                                                         self.actions[1],
                                                                                         self.actions[2],
                                                                                         self.reward))
        self.actions = np.zeros(3)
        self.played = 0

