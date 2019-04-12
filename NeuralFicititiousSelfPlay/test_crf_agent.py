# -*- coding:utf-8 -*-
from __future__ import division
from NeuralFicititiousSelfPlay.Leduc.newenv import Env
from NeuralFicititiousSelfPlay.agent.agent_cfr import AgentCFR
import numpy as np
import random
import time
import matplotlib.pyplot as plt


def train(env, player1, player2, battle_count):
    players = [player1, player2]
    dealer = random.randint(0, 1)
    player1_win_pot = []
    player2_win_pot = []

    for i in range(battle_count):
        if dealer == 0: # 每局开始互换大小盲注的位置
            dealer = 1
        else:
            dealer = 0  # 表示小盲注的位置
        # Set dealer, reset env and pass dealer to it
        env.reset(dealer)

        lhand = 1 if dealer == 0 else 0 # dealer ;小盲注 lhand :大盲注
        # Observe initial state for dealer
        d_s = env.get_state(dealer)[-1]

        terminated = False
        first_round = True
        d_t = False
        l_t = False

        while not terminated:
            actual_round = env.round_index()
            if first_round and not d_t:  # 游戏开始小盲注首先决策
                d_t = players[dealer].play(dealer, s2=d_s, batch=i) # 表示小盲注玩家是否结束游戏
                first_round = False
            elif not first_round and not d_t:
                d_t = players[dealer].play(dealer,batch=i)

            if not l_t:
                l_t = players[lhand].play(lhand,batch=i)

            if actual_round == env.round_index() and not d_t:
                d_t = players[dealer].play(dealer,batch=i)

            if d_t and l_t:
                terminated = True

        if i > 150 and i % 100 == 0:
            print("================ Stats {0}th ==================".format(i))
            for player in players:
                player.sampled_actions()
            player1_win_pot.append(players[0].reward / i)
            player2_win_pot.append(players[1].reward / i)

    f4, ax4 = plt.subplots(figsize=(14, 10))
    avg = [0] * len(player1_win_pot)
    ax4.plot(player1_win_pot, label="player0")
    ax4.plot(player2_win_pot, label="player1")
    ax4.plot(avg, color='r')
    plt.legend()
    plt.xlabel('battle count')
    plt.ylabel('player win pot')
    f4.savefig('test_player_win.png', dpi=100, bbox_inches='tight')

def main():

    # initialize env
    env = Env()
    np.random.seed(1234)
    battle_count = 1000000
    # initialize players
    player1 = AgentCFR('Player0', env)
    player2 = AgentCFR('Player1', env)
    train(env, player1, player2, battle_count)


if __name__ == '__main__':

    start_time = time.time()

    main()

    print("============= run time =========")
    print(time.time() - start_time)