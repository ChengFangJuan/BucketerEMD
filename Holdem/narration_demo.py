# -*- coding:utf-8 -*-
from Holdem.table import Table
from Holdem.templates import simulate, BasicPlayer
from sklearn.ensemble import GradientBoostingRegressor

if __name__ == '__main__':

    t = Table(smallBlind=1, bigBlind=2, maxBuyIn=200)

    players = []
    for i in range(2):
        # r表示回归算法
        # name表示玩家的名字
        r = GradientBoostingRegressor() # 随机梯度boosting回归，即r表示回归算法
        name = 'Player ' + str(i + 1)
        p = BasicPlayer(name=name, reg=r, bankroll=10 ** 6, nRaises=10, rFactor=.7, memory=10 ** 5)
        players.append(p)

    for p in players:
        t.addPlayer(p)

    # simulate 'nHands' hands
    # begin training after 'firstTrain' hands
    # before which players take random actions and explore state space
    # players train every 'nTrain' hands after 'firstTrain'
    # players cash out/ buy in every 'nBuyIn' hands
    # table narrates each hands if 'vocal' is True
    simulate(t, nHands=10000, firstTrain=2000, nTrain=1000, nBuyIn=10)
    simulate(t, nHands=20, nBuyIn=10, vocal=True)

