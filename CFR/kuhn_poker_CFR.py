# -*- coding:utf-8 -*-

import random
PASS = 0
BET = 1
NUM_ACTIONS = 2 # kukn_poker 玩家每次决策的合法动作为pass 或者 bet

class Node():
    def __init__(self):
        self.left = None
        self.right = None
        self.infoSet = ""
        self.regretSum = [0.0] * NUM_ACTIONS # 累积后悔值
        self.strategy = [0.0] * NUM_ACTIONS  # 保存策略
        self.strategySum = [0.0] * NUM_ACTIONS # 累积策略

    # 计算策略，后悔值匹配动作，累积策略
    def getStrategy(self,realizationWeight):
        normalizingSum = 0
        for a in range(NUM_ACTIONS):
            self.strategy[a] = self.regretSum[a] if self.regretSum[a] > 0 else 0
            normalizingSum += self.strategy[a]
        for a in range(NUM_ACTIONS):
            if normalizingSum > 0:
                self.strategy[a] /= normalizingSum
            else:
                self.strategy[a] = 1.0 / NUM_ACTIONS
            self.strategySum[a] += realizationWeight * self.strategy[a]
        return self.strategy

    # 标准化策略
    def getAverageStrategy(self):
        avgStrategy = [0.0] * NUM_ACTIONS
        normalizingSum = 0
        for a in range(NUM_ACTIONS):
            normalizingSum += self.strategySum[a]
        for a in range(NUM_ACTIONS):
            if normalizingSum > 0:
                avgStrategy[a] = self.strategySum[a] / normalizingSum
            else:
                avgStrategy[a] = 1.0 / NUM_ACTIONS
        return avgStrategy

    def getInfo(self):
        return self.infoSet + ": " + str(self.getAverageStrategy())

def cfr(cards, history, p0, p1):
    plays = len(history)

def train(iterations):
    cards = [1, 2, 3]
    freqOfFirstCard = [0, 0, 0]
    util = 0.0
    for i in range(iterations):
        # Shuffle cards
        for c1 in range(len(cards) - 1, -1, -1):
            c2 = random.randint(0, c1)
            temp = cards[c1]
            cards[c1] = cards[c2]
            cards[c2] = temp
        print(i + 1, cards)
        # util += cfr(cards, "", 1, 1)
    # print("Average game value: " + util / iterations)
    # Node traversal

if __name__ == "__main__":
    train(10)